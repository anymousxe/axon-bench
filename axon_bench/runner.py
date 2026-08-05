"""AXE runner — scores one model against the selected task subset.

Text tasks are matched by whole-token containment after normalisation
(lowercased, accents stripped, punctuation removed). Coding tasks are
executed: the last fenced python block is extracted, run in a timeout-bounded
subprocess, and its output compared against the expected result.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass

from .client import BenchError, chat_completion
from .tasks import Task

FENCE_RE = re.compile(r"```(?:python|py)?\s*\n([\s\S]*?)```", re.IGNORECASE)

CODE_TEMPLATE = """\
import sys
{code}
try:
    result = {test_call}
except Exception as exc:
    print("AXE_ERROR:" + type(exc).__name__)
    sys.exit(0)
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
    if stripped.startswith("def ") or "\ndef " in stripped:
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
    if task.category == "coding":
        code = extract_code(response)
        if code is None:
            return False, "no python code block in response"
        for required in task.code_checks:
            if required not in code:
                return False, f"missing required construct: {required!r}"
        output, error = run_code(code, task.test_call, code_timeout)
        if error:
            return False, error
        return output == task.answer, f"returned {output}; expected {task.answer}"
    return text_passed(task, response)


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
        except BenchError as error:
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
