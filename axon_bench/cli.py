"""axon-bench CLI — run AXE against any OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import sys

from .runner import run_bench, to_json
from .tasks import select

VERSION = "1.0.0"

EXAMPLE = """\
examples:
  axon-bench https://api.openai.com/v1 --model gpt-4o --api-key sk-...
  axon-bench http://localhost:11434/v1 --model llama3.1:8b
  axon-bench https://axon-chat-nu.vercel.app/api/v1 --model axon-1.7 --api-key axk_...
  axon-bench URL --model NAME --pro               # adversarial subset only
  axon-bench URL --model NAME --category coding --json > out.json
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
    parser.add_argument("--pro", action="store_true", help="run the adversarial AXE-Pro subset instead of standard AXE")
    parser.add_argument("--category", "-c", choices=["general", "coding", "reasoning"], help="restrict to one category")
    parser.add_argument("--limit", "-n", type=int, default=None, help="run at most N tasks (per category)")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--code-timeout", type=float, default=10.0, help="seconds allowed per coding task execution")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON instead of the report")
    parser.add_argument("--version", action="version", version=f"axon-bench {VERSION} (AXE v1)")
    args = parser.parse_args(argv)

    tasks = select(category=args.category, pro=args.pro)
    if args.limit is not None:
        tasks = tasks[: args.limit]
    if not tasks:
        print("no tasks selected", file=sys.stderr)
        return 2

    track = "AXE-Pro" if args.pro else "AXE"

    if not args.json:
        print(f"AXE v1 · {track} · {len(tasks)} tasks · model: {args.model}")

    def progress(done: int, total: int, task, passed: bool) -> None:
        if args.json:
            return
        mark = "✓" if passed else "✗"
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
        progress=progress,
    )

    if args.json:
        print(to_json(result))
        return 0

    print()
    print(f"{'=' * 44}")
    print(f"{track} results — {result.model}")
    print(f"{'=' * 44}")
    for category in ("general", "coding", "reasoning"):
        score = result.category_score(category)
        if score is None:
            continue
        print(f"  {CATEGORY_LABELS[category]:<11} {score:5.1f}")
    print(f"{'-' * 44}")
    print(f"  {'Overall':<11} {result.overall():5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
