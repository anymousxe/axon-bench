"""AXE runner — scores one model against the selected task subset.

Text tasks are matched by whole-token containment after normalisation
(lowercased, accents stripped, punctuation removed). Coding tasks are
verified, never eyeballed: the last fenced code block (python, typescript,
sql, or bare) is extracted; tasks with a `test_call` are executed in a
timeout-bounded subprocess and compared exactly, the rest are checked for
the required `code_checks` constructs. One failing request or crashing task
cannot abort the run.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .client import BenchError, chat_completion
from .tasks import Task

FENCE_RE = re.compile(r"```[ \t]*[a-zA-Z0-9+#._-]*[ \t]*\r?\n([\s\S]*?)```", re.IGNORECASE)

CODE_TEMPLATE = """\
import contextlib
import io
space = {{"__name__": "__main__"}}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile({code!r}, "<submission>", "exec"), space)
        result = eval({test_call!r}, space)
except Exception as exc:
    print("AXE_ERROR:" + type(exc).__name__)
    raise SystemExit(0)
print(repr(result))
"""


@dataclass
class TaskResult:
    task: Task
    passed: bool
    detail: str
    response: str
    seconds: float


@dataclass
class BenchResult:
    model: str
    track: str  # AXE | AXE-Pro
    results: list[TaskResult]

    def category_score(self, category: str) -> float | None:
        rows = [r for r in self.results if r.task.category == category]
        if not rows:
            return None
        return 100.0 * sum(1 for r in rows if r.passed) / len(rows)

    def overall(self) -> float:
        if not self.results:
            return 0.0
        return 100.0 * sum(1 for r in self.results if r.passed) / len(self.results)


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def text_passed(task: Task, response: str) -> tuple[bool, str]:
    haystack = normalise(response).split()
    for candidate in (task.answer, *task.aliases):
        needle = normalise(candidate).split()
        if not needle:
            continue
        span = len(needle)
        for i in range(len(haystack) - span + 1):
            if haystack[i : i + span] == needle:
                return True, f"matched '{candidate}'"
    return False, f"expected one of {[task.answer, *task.aliases]}; response started: {response[:120]!r}"


def extract_code(response: str) -> str | None:
    blocks = FENCE_RE.findall(response)
    if blocks:
        return blocks[-1].strip()
    stripped = response.strip()
    for opener in ("def ", "class ", "function ", "interface ", "type ", "SELECT", "select", "WITH", "with"):
        if stripped.startswith(opener) or f"\n{opener}" in stripped:
            return stripped
    return None


def run_code(code: str, test_call: str, timeout: float) -> tuple[str | None, str]:
    program = CODE_TEMPLATE.format(code=code, test_call=test_call)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", program],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, f"execution timed out after {timeout}s"
    if proc.returncode != 0:
        stderr = proc.stderr.strip().splitlines()
        return None, f"crashed: {stderr[-1] if stderr else 'unknown error'}"
    output = proc.stdout.strip()
    if not output:
        return None, "no output from test call"
    return output, ""


def score_task(task: Task, response: str, code_timeout: float) -> tuple[bool, str]:
    wants_code = task.kind == "code" or bool(task.test_call) or bool(task.code_checks)
    if not wants_code:
        return text_passed(task, response)
    code = extract_code(response)
    if code is None:
        return False, "no code block in response"
    lowered = code.lower()
    for required in task.code_checks:
        if required.lower() not in lowered:
            return False, f"missing required construct: {required!r}"
    if not task.test_call:
        return True, "required constructs present" if task.code_checks else "code block present"
    output, error = run_code(code, task.test_call, code_timeout)
    if error:
        return False, error
    return output == task.answer, f"returned {output}; expected {task.answer}"


def run_bench(
    base_url: str,
    api_key: str,
    model: str,
    tasks: list[Task],
    *,
    track: str,
    temperature: float,
    max_tokens: int,
    code_timeout: float,
    progress=None,
) -> BenchResult:
    results: list[TaskResult] = []
    for index, task in enumerate(tasks):
        started = time.monotonic()
        detail = ""
        response = ""
        passed = False
        try:
            response = chat_completion(
                base_url,
                api_key,
                model,
                task.prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            passed, detail = score_task(task, response, code_timeout)
        except Exception as error:  # one bad request must not kill the run
            detail = f"request failed: {error}"
        results.append(
            TaskResult(
                task=task,
                passed=passed,
                detail=detail,
                response=response,
                seconds=time.monotonic() - started,
            )
        )
        if progress:
            progress(index + 1, len(tasks), task, passed)
    return BenchResult(model=model, track=track, results=results)


def to_json(result: BenchResult) -> str:
    return json.dumps(
        {
            "bench": "AXE v1",
            "track": result.track,
            "model": result.model,
            "overall": round(result.overall(), 1),
            "scores": {
                category: (
                    round(result.category_score(category), 1)
                    if result.category_score(category) is not None
                    else None
                )
                for category in ("general", "coding", "reasoning")
            },
            "tasks": [
                {
                    "prompt": r.task.prompt,
                    "category": r.task.category,
                    "pro": r.task.pro,
                    "passed": r.passed,
                    "detail": r.detail,
                    "seconds": round(r.seconds, 2),
                }
                for r in result.results
            ],
        },
        indent=2,
    )

def render_report(result: BenchResult) -> str:
    """Human-readable report: per-category accuracy, overall score, timing, per-task table."""
    header = f"AXE v1 · {result.track} · {len(result.results)} tasks · {result.model}"
    lines = [header, "=" * len(header), f"{'Category':<10} {'Pass':>7} {'Score':>7}"]
    total = 0
    for category in ("general", "coding", "reasoning"):
        rows = [r for r in result.results if r.task.category == category]
        if not rows:
            continue
        passed = sum(r.passed for r in rows)
        total += passed
        lines.append(f"{category:<10} {f'{passed}/{len(rows)}':>7} {100.0 * passed / len(rows):>6.1f}%")
    lines.append("-" * 26)
    lines.append(f"{'Overall':<10} {f'{total}/{len(result.results)}':>7} {result.overall():>6.1f}%")
    if result.results:
        seconds = [r.seconds for r in result.results]
        lines.append("")
        lines.append(f"time: total {sum(seconds):.1f}s · median {sorted(seconds)[len(seconds) // 2]:.2f}s · slowest {max(seconds):.2f}s")
        lines.extend(("", "Task results"))
        for r in result.results:
            mark = "✓" if r.passed else "✗"
            prompt = r.task.prompt if len(r.task.prompt) <= 70 else r.task.prompt[:69] + "..."
            lines.append(f"  {mark} {r.task.category:<9} {r.seconds:5.2f}s  {prompt}")
    return "\n".join(lines)


def write_report(result: BenchResult, path: str) -> None:
    """Write the rendered report to path, creating parent directories as needed."""
    target = Path(path)
    if target.parent != Path("."):
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result) + "\n", encoding="utf-8")
