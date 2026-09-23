"""Revisioned AXE runner with strict text scoring and executed Python cases.

Subprocess resource limits reduce accidental damage; they are NOT an OS sandbox.
Run untrusted submissions in an externally isolated, disposable environment.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .client import chat_completion
from .tasks import DIFFICULTIES, TASK_HASH, TASK_REVISION, Task

FENCE_RE = re.compile(r"```[ \t]*(?:python|python3|py)?[ \t]*\r?\n([\s\S]*?)```", re.IGNORECASE)
OUTPUT_LIMIT = 1024 * 1024
CODE_TEMPLATE = """\
import contextlib
import resource
resource.setrlimit(resource.RLIMIT_CPU, ({cpu}, {cpu}))
resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
class Sink:
    def write(self, text):
        return len(text)
    def flush(self):
        pass
space = {{"__name__": "__submission__"}}
try:
    with contextlib.redirect_stdout(Sink()), contextlib.redirect_stderr(Sink()):
        exec(compile({code!r}, "<submission>", "exec"), space)
        result = eval({test_call!r}, space)
except BaseException as exc:
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
    error: bool = False


@dataclass
class BenchResult:
    model: str
    track: str
    results: list[TaskResult]
    temperature: float | None = None
    max_tokens: int | None = None
    code_timeout: float | None = None
    reasoning_effort: str | None = None
    enhancement: bool | None = None

    def category_score(self, category: str) -> float | None:
        rows = [r for r in self.results if r.task.category == category]
        return 100.0 * sum(r.passed for r in rows) / len(rows) if rows else None

    def overall(self) -> float:
        return 100.0 * sum(r.passed for r in self.results) / len(self.results) if self.results else 0.0

    @property
    def request_errors(self) -> int:
        return sum(r.error for r in self.results)


def normalise(text: str) -> str:
    """Ignore only Unicode composition, case, and whitespace, not semantic signs."""
    normalized = " ".join(unicodedata.normalize("NFC", text).casefold().split())
    return re.sub(r"\s*([,/])\s*", r"\1", normalized)


def text_passed(task: Task, response: str) -> tuple[bool, str]:
    actual = normalise(response)
    for candidate in (task.answer, *task.aliases):
        if actual and actual == normalise(candidate):
            return True, "exact answer"
    return False, f"expected one of {[task.answer, *task.aliases]}; received {response[:160]!r}"


def extract_code(response: str) -> str | None:
    blocks = FENCE_RE.findall(response)
    if blocks:
        return "\n\n".join(block.strip() for block in blocks)
    stripped = response.strip()
    try:
        module = ast.parse(stripped)
    except SyntaxError:
        return None
    return stripped if any(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in module.body) else None


def run_code(code: str, test_call: str, timeout: float) -> tuple[str | None, str]:
    if not math.isfinite(timeout) or timeout <= 0:
        return None, "code timeout must be positive and finite"
    program = CODE_TEMPLATE.format(code=code, test_call=test_call, cpu=max(1, math.ceil(timeout)))
    # Do not inherit API tokens/environment or the repository working directory.
    # -I/-S disables user paths and site initialization. These are not a sandbox.
    with tempfile.TemporaryDirectory(prefix="axe-") as directory:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            proc = subprocess.Popen(
                [sys.executable, "-I", "-S", "-c", program], cwd=directory,
                env={}, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                start_new_session=True,
            )
            timed_out = False
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
            finally:
                # Also terminate descendants after an early parent exit.
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
            if timed_out:
                return None, f"execution timed out after {timeout}s"
            stdout.seek(0)
            raw = stdout.read(OUTPUT_LIMIT + 1)
            if len(raw) > OUTPUT_LIMIT:
                return None, "execution output exceeded limit"
            stderr.seek(0)
            error_text = stderr.read(4096).decode("utf-8", errors="replace").strip()
            if proc.returncode != 0:
                return None, f"execution failed ({proc.returncode}): {error_text[-300:]}"
            output = raw.decode("utf-8", errors="replace").strip()
            if output.startswith("AXE_ERROR:"):
                return None, output
            if not output:
                return None, "no output from test call"
            return output, ""


def _same_value(actual, expected) -> bool:
    # Numeric representation differences (2 vs 2.0) are harmless; bool is not 1.
    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return actual == expected
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(_same_value(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(_same_value(actual[k], v) for k, v in expected.items())
    return actual == expected


def score_task(task: Task, response: str, code_timeout: float = 10.0) -> tuple[bool, str]:
    if task.kind != "code" and not task.test_call and not task.code_checks:
        return text_passed(task, response)
    if not task.test_call:
        return False, "coding task has no executable cases; construct-only grading is unsupported"
    code = extract_code(response)
    if code is None:
        return False, "no Python implementation in response"
    output, error = run_code(code, task.test_call, code_timeout)
    if error:
        return False, error
    try:
        actual, expected = ast.literal_eval(output), ast.literal_eval(task.answer)
    except (ValueError, SyntaxError, TypeError, RecursionError):
        return False, f"nonliteral result: {output!r}"
    passed = _same_value(actual, expected)
    return passed, "all executable cases passed" if passed else f"returned {output}; expected {task.answer}"


def run_bench(base_url: str, api_key: str, model: str, tasks: list[Task], *,
              track: str, temperature: float, max_tokens: int, code_timeout: float,
              progress=None, reasoning_effort: str | None = None,
              enhancement: bool | None = None) -> BenchResult:
    results = []
    for index, task in enumerate(tasks):
        started = time.monotonic()
        response, detail, passed, request_error = "", "", False, False
        try:
            response = chat_completion(base_url, api_key, model, task.prompt,
                                       temperature=temperature, max_tokens=max_tokens,
                                       reasoning_effort=reasoning_effort, enhancement=enhancement)
        except Exception as error:
            request_error = True
            detail = f"request failed: {error}"
        else:
            try:
                passed, detail = score_task(task, response, code_timeout)
            except Exception as error:
                # Infrastructure/grader exceptions invalidate a comparison just as transport failures do.
                request_error = True
                detail = f"grading failed: {type(error).__name__}: {error}"
        results.append(TaskResult(task, passed, detail, response, time.monotonic() - started, request_error))
        if progress:
            progress(index + 1, len(tasks), task, passed)
    return BenchResult(model, track, results, temperature, max_tokens, code_timeout, reasoning_effort, enhancement)


def to_json(result: BenchResult) -> str:
    return json.dumps({
        "bench": "AXE v1", "version": "1.1.1", "taskRevision": TASK_REVISION, "taskHash": TASK_HASH,
        "track": result.track, "model": result.model, "overall": result.overall(),
        "temperature": result.temperature, "maxOutputTokens": result.max_tokens,
        "codeTimeout": result.code_timeout,
        "reasoning": result.reasoning_effort, "enhancement": result.enhancement,
        "requestErrors": result.request_errors, "publishable": bool(result.results) and result.request_errors == 0,
        "scores": {c: result.category_score(c) for c in ("general", "coding", "reasoning")},
        "byDifficulty": {d: {"passed": sum(r.passed for r in result.results if r.task.difficulty == d),
                             "total": sum(r.task.difficulty == d for r in result.results)} for d in DIFFICULTIES},
        "tasks": [{"id": r.task.id, "prompt": r.task.prompt, "category": r.task.category,
                   "pro": r.task.pro, "difficulty": r.task.difficulty, "passed": r.passed,
                   "detail": r.detail, "details": r.detail, "response": r.response,
                   "error": r.error, "status": "error" if r.error else "pass" if r.passed else "fail",
                   "seconds": r.seconds} for r in result.results],
    }, indent=2)


def render_report(result: BenchResult) -> str:
    header = f"AXE v1 · {result.track} · {len(result.results)} tasks · {result.model}"
    lines = [header, "=" * len(header), f"Task revision: {TASK_REVISION}", f"Task hash: {TASK_HASH}"]
    if result.request_errors:
        lines.append(f"INVALID FOR COMPARISON: {result.request_errors} request/grading errors; rerun failed requests.")
    lines.append(f"{'Category':<10} {'Pass':>7} {'Score':>7}")
    for category in ("general", "coding", "reasoning"):
        rows = [r for r in result.results if r.task.category == category]
        if rows:
            passed = sum(r.passed for r in rows)
            lines.append(f"{category:<10} {f'{passed}/{len(rows)}':>7} {100.0 * passed / len(rows):>6.1f}%")
    total = sum(r.passed for r in result.results)
    lines.extend(["-" * 26, f"{'Overall':<10} {f'{total}/{len(result.results)}':>7} {result.overall():>6.1f}%"])
    for difficulty in DIFFICULTIES:
        rows = [r for r in result.results if r.task.difficulty == difficulty]
        if rows:
            lines.append(f"{difficulty:<10} {sum(r.passed for r in rows)}/{len(rows)}")
    if result.results:
        seconds = sorted(r.seconds for r in result.results)
        lines.append(f"time: total {sum(seconds):.1f}s · median {seconds[len(seconds)//2]:.2f}s · slowest {max(seconds):.2f}s")
        lines.append("Task results")
        for r in result.results:
            status = "ERROR" if r.error else "PASS" if r.passed else "FAIL"
            lines.append(f"  {status} {r.task.id} {r.task.difficulty} {r.seconds:.2f}s")
    return "\n".join(lines)


def write_report(result: BenchResult, path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result) + "\n", encoding="utf-8")
