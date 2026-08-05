"""Offline verification: scoring logic + a mock OpenAI-compatible server."""

import contextlib
import io
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, ".")

from axon_bench.runner import extract_code, normalise, run_code, score_task, text_passed  # noqa: E402
from axon_bench.tasks import CODING, GENERAL, REASONING, TASKS, select  # noqa: E402

failures = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok  {name}")
    else:
        print(f" FAIL {name} {detail}")
        failures.append(name)


# --- 1. task bank integrity ---
print("task bank:")
check("70 tasks total", len(TASKS) == 70, f"got {len(TASKS)}")
check("30 general", len(GENERAL) == 30, f"got {len(GENERAL)}")
check("20 coding", len(CODING) == 20, f"got {len(CODING)}")
check("20 reasoning", len(REASONING) == 20, f"got {len(REASONING)}")
check("20 pro", sum(1 for t in TASKS if t.pro) == 20)
check("50 standard", len(select(pro=False)) == 50)
check("select category works", len(select(category="coding", pro=True)) == 5)
for task in CODING:
    if not task.test_call or not task.code_checks:
        check(f"coding task has test_call+checks: {task.prompt[:40]}", False)
        break
else:
    check("every coding task has test_call and code_checks", True)

# --- 2. code extraction and execution ---
print("code scoring:")
resp = "Here you go:\n```python\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)\n```\nDone."
code = extract_code(resp)
check("extract fenced block", code is not None and "def factorial" in code)
out, err = run_code(code or "", "factorial(5)", 10)
check("execute submitted code", out == "120", f"out={out} err={err}")

bad = "```python\ndef factorial(n):\n    return n\n```"
out, err = run_code(extract_code(bad) or "", "factorial(5)", 10)
check("wrong code executes but scores fail", out == "5", f"out={out} err={err}")
task = next(t for t in CODING if "factorial" in t.prompt)
passed, detail = score_task(task, resp, 10)
check("score_task pass", passed, detail)
passed, detail = score_task(task, bad, 10)
check("score_task fail on wrong answer", not passed, detail)
passed, detail = score_task(task, "I don't write code.", 10)
check("score_task fail on no code", not passed, detail)

infinite = "```python\ndef factorial(n):\n    while True: pass\n```"
out, err = run_code(extract_code(infinite) or "", "factorial(5)", 2)
check("timeout caught", out is None and "timed out" in err, f"err={err}")

# --- 3. text matching ---
print("text scoring:")
canberra = next(t for t in GENERAL if "capital of Australia" in t.prompt)
check("plain match", text_passed(canberra, "The capital of Australia is Canberra.")[0])
check("case-insensitive", text_passed(canberra, "CANBERRA")[0])
check("punct stripped", text_passed(canberra, "Canberra!")[0])
check("no false positive", not text_passed(canberra, "I don't know")[0])
marquez = next(t for t in GENERAL if "One Hundred Years" in t.prompt)
check("alias match", text_passed(marquez, "Gabriel García Márquez wrote it.")[0])
saturn = next(t for t in GENERAL if "moons" in t.prompt)
check("no substring trap (jupiter vs saturn)", not text_passed(saturn, "Jupiter used to have the most")[0])

# --- 4. mock server end-to-end ---
print("end-to-end vs mock server:")

ANSWERS = {
    "capital of Australia": "The capital of Australia is Canberra.",
    "most confirmed moons": "Saturn has the most confirmed moons.",
    "One Hundred Years": "Gabriel Garcia Marquez wrote it.",
    "Berlin Wall fall": "The Berlin Wall fell in 1989.",
    "fizzbuzz": "```python\ndef fizzbuzz(n):\n    out = []\n    for i in range(1, n + 1):\n        if i % 15 == 0:\n            out.append('FizzBuzz')\n        elif i % 3 == 0:\n            out.append('Fizz')\n        elif i % 5 == 0:\n            out.append('Buzz')\n        else:\n            out.append(str(i))\n    return out\n```",
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


server = HTTPServer(("127.0.0.1", 8791), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

from axon_bench.cli import main  # noqa: E402

rc = main(["http://127.0.0.1:8791/v1", "--model", "mock-1", "--category", "coding", "--limit", "2"])
check("cli coding run exits 0", rc == 0)
rc = main(["http://127.0.0.1:8791/v1", "--model", "mock-1", "--category", "general", "--limit", "4"])
check("cli general run exits 0", rc == 0)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    main(["http://127.0.0.1:8791/v1", "--model", "mock-1", "--category", "reasoning", "--limit", "1", "--json"])
parsed = json.loads(buf.getvalue())
check("json output structure", parsed["scores"]["reasoning"] == 100.0, str(parsed["scores"]))
server.shutdown()

print()
if failures:
    print(f"FAILED: {failures}")
    sys.exit(1)
print("ALL CHECKS PASSED")
