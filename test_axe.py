"""Offline behavioral regressions and independent reference-case verification.

Run with pytest or `python test_axe.py`. No model endpoint is contacted.
"""
import contextlib
import io
import json
import os
import threading
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from axon_bench.cli import main
from axon_bench.runner import BenchResult, TaskResult, run_bench, run_code, score_task, to_json
from axon_bench.tasks import CODING, DIFFICULTIES, SOLUTIONS, TASKS, Task, select, select_tasks


def test_bank_integrity():
    assert len(TASKS) == 286
    assert len({t.id for t in TASKS}) == len(TASKS)
    assert len({t.prompt for t in TASKS}) == len(TASKS)
    assert all(t.id and t.reference and t.difficulty in DIFFICULTIES for t in TASKS)
    for pro in (False, True):
        rows = select(pro=pro)
        assert Counter(t.category for t in rows) == {"general": 48, "coding": 48, "reasoning": 47}
        assert rows == select_tasks(pro=pro)
        assert {t.difficulty for t in rows} >= {"medium", "hard", "expert"}
    assert not set(t.id for t in select()) & set(t.id for t in select(pro=True))
    assert all(t.kind == "code" and len(t.test_cases) >= 4 and t.test_call for t in CODING)


def test_exact_scoring_rejects_candidate_dumps_and_negation():
    task = Task("Name the city", "Canberra", "general")
    assert score_task(task, " CANBERRA\n")[0]
    for response in ("not Canberra", "Sydney or Canberra", "Canberra, Sydney", "Canberran", "I cannot answer"):
        assert not score_task(task, response)[0], response


def test_signs_and_punctuation_keep_meaning():
    negative = Task("Signed value", "-7", "reasoning")
    assert score_task(negative, "-7")[0]
    assert not score_task(negative, "7")[0]
    assert not score_task(negative, "+7")[0]
    blood = Task("Exact group", "O-negative", "general", aliases=("O-",))
    assert score_task(blood, "O-")[0]
    for response in ("O", "O+", "O-positive", "O-negative or O-positive"):
        assert not score_task(blood, response)[0]
    decimal = Task("decimal", "0.5", "reasoning")
    assert not score_task(decimal, "0 5")[0]
    pair = Task("pair", "1,4", "reasoning")
    assert score_task(pair, "1, 4")[0]
    fraction = Task("fraction", "1/2", "reasoning")
    assert score_task(fraction, "1 / 2")[0]
    assert not score_task(decimal, "0/5")[0]


def test_reasoning_final_answer_is_scored_not_explanation_format():
    task = Task("How many edges?", "14", "reasoning")
    assert score_task(task, "Sum of degrees is 28, so divide by two.\n\n14")[0]
    assert score_task(task, "Derivation gives 14.\nFinal answer: **14**.")[0]
    assert not score_task(task, "14\n13")[0]
    assert not score_task(task, "13\n14")[0]
    assert not score_task(task, "Possible answers: 12, 13, 14\n14")[0]
    assert not score_task(task, "The final answer is not **14**.")[0]
    assert not score_task(task, "Compute the degrees.\nFinal answer: 13")[0]
    fraction = Task("Conditional probability?", "1/3", "reasoning")
    assert score_task(fraction, "Divide the conditional counts.\nSo the answer is **1/3**.")[0]
    assert score_task(fraction, r"\boxed{\frac{1}{3}}")[0]
    assert not score_task(fraction, "1/3 or 2/3")[0]


def test_all_cases_must_pass_not_just_example():
    task = Task("Implement absolute", "[3, 0, 4]", "coding", kind="code",
                test_call="[absolute(-3), absolute(0), absolute(4)]")
    assert score_task(task, "def absolute(n):\n    return abs(n)")[0]
    assert not score_task(task, "def absolute(n):\n    return 3")[0]
    assert not score_task(task, "def absolute(n):\n    return -n")[0]
    assert not score_task(task, "```python\n# def absolute; return abs(n)\n```")[0]


def test_code_results_use_values_not_dict_insertion_order():
    task = Task("mapping", "{'a': [1, False], 'b': 2}", "coding", kind="code", test_call="f()")
    assert score_task(task, "def f():\n    return {'b': 2.0, 'a': [1, False]}")[0]
    assert not score_task(task, "def f():\n    return {'b': 2, 'a': [1, 0]}")[0]
    assert not score_task(task, "def f():\n    return {'b': 2, 'a': (1, False)}")[0]


def test_construct_only_code_cannot_pass():
    task = Task("query", "whatever", "coding", kind="code", code_checks=("SELECT",))
    assert not score_task(task, "```sql\nSELECT wrong FROM missing\n```")[0]


def test_execution_is_bounded_and_ignores_debug_prints():
    out, error = run_code("print('setup')\ndef f():\n    print('debug')\n    return 19", "f()", 3)
    assert (out, error) == ("19", "")
    out, error = run_code("def f():\n    while True: pass", "f()", 0.1)
    assert out is None and error
    out, error = run_code("def f():\n    raise ValueError('bad')", "f()", 3)
    assert out is None and error
    with patch.dict(os.environ, {"AXE_TEST_SECRET": "must-not-inherit"}):
        out, error = run_code("import os\ndef f():\n    return os.getenv('AXE_TEST_SECRET')", "f()", 3)
    assert (out, error) == ("None", "")


def test_reference_solutions():
    for task in CODING:
        passed, detail = score_task(task, SOLUTIONS[task.solution_name], 10)
        assert passed, f"{task.id}: {detail}"


def test_refusals_are_wrong_but_transport_errors_invalidate_run():
    rows = [Task("one", "yes", "general"), Task("two", "yes", "general"), Task("three", "yes", "general")]
    with patch("axon_bench.runner.chat_completion", side_effect=["yes", "I cannot answer", RuntimeError("offline")]):
        result = run_bench("http://unused", "", "model", rows, track="AXE", temperature=0, max_tokens=16, code_timeout=3)
    assert [r.passed for r in result.results] == [True, False, False]
    assert [r.error for r in result.results] == [False, False, True]
    assert result.overall() == 100 / 3
    report = json.loads(to_json(result))
    assert report["publishable"] is False
    assert report["requestErrors"] == 1
    assert report["tasks"][1]["status"] == "fail"
    assert report["tasks"][2]["status"] == "error"


def test_scores_are_measured_not_capped():
    task = Task("x", "y", "general")
    result = BenchResult("any", "AXE", [TaskResult(task, True, "", "y", 0)])
    assert result.overall() == 100
    assert json.loads(to_json(result))["overall"] == 100
    result.results[0].passed = False
    assert result.overall() == 0


def test_cli_real_http_and_difficulty_selection():
    tasks = [Task("first", "yes", "general", id="fixture-one", difficulty="hard"),
             Task("second", "no", "reasoning", id="fixture-two", difficulty="hard")]

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            answer = "yes" if body["messages"][0]["content"] == "first" else "wrong"
            encoded = json.dumps({"choices": [{"message": {"content": answer}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    output = io.StringIO()
    try:
        with patch("axon_bench.cli.select", return_value=tasks), contextlib.redirect_stdout(output):
            status = main([f"http://127.0.0.1:{server.server_port}/v1", "--model", "fixture", "--difficulty", "hard", "--json"])
        report = json.loads(output.getvalue())
        assert status == 0 and report["publishable"]
        assert report["overall"] == 50
        assert report["byDifficulty"]["hard"] == {"passed": 1, "total": 2}
        assert report["tasks"][0]["response"] == "yes"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print(f"PASS {name}")
