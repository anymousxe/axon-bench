"""Offline verification: bank integrity, scoring logic, reference solutions,
and a mock-server end-to-end run. No network beyond a localhost mock.

Runs under pytest (``python -m pytest -q``) or directly (``python test_axe.py``).
"""

import contextlib
import io
import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, ".")

import axon_bench  # noqa: E402
from axon_bench.runner import (  # noqa: E402
    BenchResult,
    TaskResult,
    extract_code,
    normalise,
    render_report,
    run_bench,
    run_code,
    score_task,
    text_passed,
    write_report,
)
from axon_bench.tasks import CODING, GENERAL, REASONING, SOLUTIONS, TASKS, Task, select  # noqa: E402

MOCK_PORT = 8791


def test_bank_integrity():
    assert axon_bench.__version__ == "1.1.0"
    assert len(TASKS) >= 150, len(TASKS)
    assert len(GENERAL) >= 60 and len(CODING) >= 45 and len(REASONING) >= 45
    assert sum(1 for t in TASKS if t.pro) >= 40
    prompts = [t.prompt for t in TASKS]
    assert len(prompts) == len(set(prompts)), "duplicate prompts in bank"
    for task in TASKS:
        assert task.prompt and task.answer, task
        assert task.category in ("general", "coding", "reasoning")
        assert isinstance(task.aliases, tuple) and isinstance(task.code_checks, tuple)
        if task.category == "coding":
            assert task.test_call or task.code_checks, task.prompt


def test_select_filters():
    standard = select()
    pro = select(pro=True)
    assert standard == [t for t in TASKS if not t.pro]
    assert pro and all(t.pro for t in pro)
    assert len(standard) + len(pro) == len(TASKS)
    coding_pro = select(category="coding", pro=True)
    assert coding_pro and all(t.category == "coding" and t.pro for t in coding_pro)
    assert {t.category for t in select(category="reasoning")} == {"reasoning"}


def test_code_extraction():
    blocks = {
        "```python\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)\n```": "def factorial",
        "```typescript\nfunction firstOrNull<T>(items: T[]): T | null {\n  return items[0] ?? null;\n}\n```": "firstOrNull",
        "```sql\nSELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1\n```": "OFFSET 1",
        "```\ndef fib(n):\n    return n\n```": "def fib",
        "here is one:\n```py\ndef dot(a, b):\n    return 3\n```\nthanks": "def dot",
    }
    assert extract_code("I don't write code.") is None
    for block, marker in blocks.items():
        code = extract_code(block)
        assert code is not None and marker in code, block
    out, err = run_code(extract_code(list(blocks)[0]) or "", "factorial(5)", 10)
    assert err == "" and out == "120"
    loop = "```python\ndef factorial(n):\n    while True: pass\n```"
    out, err = run_code(extract_code(loop) or "", "factorial(5)", 2)
    assert out is None and "timed out" in err, err


def test_scoring():
    factorial = next(t for t in CODING if "factorial" in t.prompt)
    passed, _ = score_task(factorial, "```python\n" + SOLUTIONS["factorial"] + "```", 10)
    assert passed
    passed, detail = score_task(factorial, "```python\ndef factorial(n):\n    return n\n```", 10)
    assert not passed and "expected" in detail
    passed, detail = score_task(factorial, "I don't write code.", 10)
    assert not passed and "no code block" in detail

    ts_task = next(t for t in CODING if "firstOrNull" in t.prompt and t.kind == "code")
    good_ts = "```typescript\nfunction firstOrNull<T>(items: T[]): T | null {\n  return items.length ? items[0] : null;\n}\n```"
    passed, detail = score_task(ts_task, good_ts, 10)
    assert passed, detail
    passed, detail = score_task(ts_task, "```typescript\nexport const pick = (x) => x[0];\n```", 10)
    assert not passed and "missing required construct" in detail

    sql_task = next(t for t in CODING if "DENSE_RANK" in t.prompt)
    low_sql = "```sql\nselect name, dense_rank() over (partition by dept order by pay desc) from employees\n```"
    passed, detail = score_task(sql_task, low_sql, 10)
    assert passed, detail

    plain = Task("Write hello", "hello", "coding")  # neither test_call nor code_checks
    passed, detail = score_task(plain, "The function returns hello.", 10)
    assert passed, detail


def test_text_scoring():
    canberra = next(t for t in GENERAL if "capital of Australia" in t.prompt)
    assert text_passed(canberra, "The capital of Australia is Canberra.")[0]
    assert text_passed(canberra, "CANBERRA")[0]
    assert text_passed(canberra, "Canberra!")[0]
    assert not text_passed(canberra, "I don't know")[0]
    marquez = next(t for t in GENERAL if "One Hundred Years" in t.prompt)
    assert text_passed(marquez, "Gabriel Garcia Marquez wrote it.")[0]
    saturn = next(t for t in GENERAL if "moons" in t.prompt)
    assert not text_passed(saturn, "Jupiter used to have the most")[0]
    assert normalise("GarçOn–Márquez!!") == "garcon marquez"


def test_reference_solutions():
    executable = [t for t in CODING if t.test_call]
    assert len(executable) >= 40, len(executable)
    for task in executable:
        name = task.test_call.split("(")[0]
        assert name in SOLUTIONS, name
        out, err = run_code(SOLUTIONS[name], task.test_call, 15)
        assert err == "", f"{name}: {err}"
        assert out == task.answer, f"{name}: {out!r} != {task.answer!r}"


def test_run_bench_isolation():
    import axon_bench.runner as runner_mod

    hard = next(t for t in REASONING if "17 times 23" in t.prompt)
    easy = Task("What is 5 plus 5?", "10", "reasoning")
    original = runner_mod.chat_completion

    def flaky(base_url, api_key, model, prompt, **kwargs):
        if "17 times 23" in prompt:
            raise RuntimeError("connection reset")
        return "10"

    runner_mod.chat_completion = flaky
    try:
        result = run_bench("", "", "fake", [hard, easy], track="AXE", temperature=0.0, max_tokens=16, code_timeout=5)
    finally:
        runner_mod.chat_completion = original
    assert len(result.results) == 2
    assert not result.results[0].passed and "request failed" in result.results[0].detail
    assert result.results[1].passed
    assert result.overall() == 50.0


def test_reports():
    factorial = next(t for t in CODING if "factorial" in t.prompt)
    other = Task("Impossible?", "nope", "general")
    result = BenchResult(
        model="mock",
        track="AXE",
        results=[
            TaskResult(task=factorial, passed=True, detail="ok", response="", seconds=0.5),
            TaskResult(task=other, passed=False, detail="nope", response="", seconds=0.25),
        ],
    )
    text = render_report(result)
    assert "AXE v1 · AXE · 2 tasks · mock" in text
    assert "coding" in text and "general" in text
    assert "✓" in text and "✗" in text
    assert "Overall" in text and "50.0%" in text
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "report.txt"
        write_report(result, str(path))
        assert path.read_text(encoding="utf-8").startswith("AXE v1")


ANSWERS = {
    "capital of Australia": "The capital of Australia is Canberra.",
    "13th President": "Millard Fillmore was the 13th President.",
    "count_words": "```python\n" + SOLUTIONS["count_words"] + "```",
    "fizzbuzz": "```python\n" + SOLUTIONS["fizzbuzz"] + "```",
    "17 times 23": "391",
}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = body["messages"][0]["content"]
        answer = "I don't know."
        for key, value in ANSWERS.items():
            if key in prompt:
                answer = value
                break
        resp = json.dumps({"choices": [{"message": {"content": answer}}]}).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, *args):
        pass


def test_end_to_end():
    from axon_bench.cli import main

    server = HTTPServer(("127.0.0.1", MOCK_PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{MOCK_PORT}/v1"

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main([url, "--model", "mock-1", "--category", "reasoning", "--limit", "1", "--json"])
        assert rc == 0
        parsed = json.loads(buf.getvalue())
        assert parsed["scores"]["reasoning"] == 100.0, parsed["scores"]
        assert parsed["tasks"][0]["pro"] is False

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main([url, "--model", "mock-1", "--category", "coding", "--limit", "2", "--json"])
        assert rc == 0
        parsed = json.loads(buf.getvalue())
        assert parsed["overall"] == 100.0, [t["detail"] for t in parsed["tasks"]]
        assert len(parsed["tasks"]) == 2

        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.txt"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = main([url, "--model", "mock-1", "--track", "pro", "--category", "general", "--limit", "1", "--json", "--report", str(report)])
            assert rc == 0
            parsed = json.loads(buf.getvalue())
            assert parsed["track"] == "AXE-Pro"
            assert parsed["tasks"][0]["pro"] is True
            assert parsed["overall"] == 100.0, parsed["tasks"][0]
            assert report.exists() and "AXE v1" in report.read_text(encoding="utf-8")
    finally:
        server.shutdown()


def _main() -> int:
    tests = [
        test_bank_integrity,
        test_select_filters,
        test_code_extraction,
        test_scoring,
        test_text_scoring,
        test_reference_solutions,
        test_run_bench_isolation,
        test_reports,
        test_end_to_end,
    ]
    failures = []
    for fn in tests:
        try:
            fn()
            print(f"  ok   {fn.__name__}")
        except AssertionError as error:
            failures.append(fn.__name__)
            print(f"  FAIL {fn.__name__}: {error}")
    print()
    if failures:
        print(f"FAILED: {failures}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
