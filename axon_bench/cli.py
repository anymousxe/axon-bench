"""axon-bench CLI — run AXE against any OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import sys

from .runner import render_report, run_bench, to_json, write_report
from .tasks import DIFFICULTIES, TASK_REVISION, Task, select

VERSION = "1.1.1"

EXAMPLE = """\
examples:
  axon-bench https://api.openai.com/v1 --model gpt-4o --api-key sk-...
  axon-bench http://localhost:11434/v1 --model llama3.1:8b
  axon-bench https://axon-chat-nu.vercel.app/api/v1 --model axon-1.8-flash --api-key axk_...
  axon-bench URL --model NAME --track pro            # independent harder track
  axon-bench URL --model NAME --category coding --json > out.json
  axon-bench URL --model NAME --limit 5 --report run.txt
"""

CATEGORY_LABELS = {"general": "General", "coding": "Coding", "reasoning": "Reasoning"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="axon-bench",
        description="AXE — the Axon Labs evaluation suite. Benchmarks any OpenAI-compatible model on general knowledge, coding, and reasoning.",
        epilog=EXAMPLE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("base_url", help="OpenAI-compatible API root, e.g. https://api.openai.com/v1")
    parser.add_argument("--model", "-m", required=True, help="model name to benchmark")
    parser.add_argument("--api-key", "-k", default="EMPTY", help="bearer token (default: EMPTY for local servers)")
    parser.add_argument("--pro", action="store_true", help="shorthand for --track pro")
    parser.add_argument("--track", "-t", choices=["axe", "pro"], default=None, help="task track to run (default: axe)")
    parser.add_argument("--category", "-c", choices=["general", "coding", "reasoning"], help="restrict to one category")
    parser.add_argument("--difficulty", choices=DIFFICULTIES, help="restrict to one difficulty level")
    parser.add_argument("--limit", "-n", type=int, default=None, help="run at most N tasks per category")
    parser.add_argument("--report", "-r", default=None, help="write the human-readable report to this file")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--code-timeout", type=float, default=10.0, help="seconds allowed per coding task execution")
    parser.add_argument("--reasoning-effort", choices=["none", "minimal", "low", "medium", "high", "xhigh", "max"], default=None)
    parser.add_argument("--enhancement", action=argparse.BooleanOptionalAction, default=None, help="Axon enhancement setting; omit for other providers")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the report")
    parser.add_argument("--version", action="version", version=f"axon-bench {VERSION} (AXE v1; tasks {TASK_REVISION})")
    args = parser.parse_args(argv)

    pro = args.pro or args.track == "pro"
    tasks = select(category=args.category, pro=pro, difficulty=args.difficulty)
    if args.limit is not None:
        counts: dict[str, int] = {}
        capped: list[Task] = []
        for task in tasks:
            counts[task.category] = counts.get(task.category, 0) + 1
            if counts[task.category] <= args.limit:
                capped.append(task)
        tasks = capped
    if not tasks:
        print("no tasks selected", file=sys.stderr)
        return 2

    track = "AXE-Pro" if pro else "AXE"

    if not args.json:
        print(f"AXE v1 · {track} · {len(tasks)} tasks · model: {args.model} · revision: {TASK_REVISION}")

    def progress(done: int, total: int, task, passed: bool) -> None:
        if args.json:
            return
        mark = "PASS" if passed else "FAIL"
        label = task.prompt[:58].replace("\n", " ")
        print(f"  [{done}/{total}] {mark} {label}")

    result = run_bench(
        args.base_url,
        args.api_key,
        args.model,
        tasks,
        track=track,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        code_timeout=args.code_timeout,
        reasoning_effort=args.reasoning_effort,
        enhancement=args.enhancement,
        progress=progress,
    )

    if args.report:
        write_report(result, args.report)
    if args.json:
        print(to_json(result))
        if args.report:
            print(f"report written to {args.report}", file=sys.stderr)
        return 1 if result.request_errors else 0

    print()
    print(render_report(result))
    if args.report:
        print(f"\nreport written to {args.report}")
    return 1 if result.request_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
