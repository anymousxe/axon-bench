# axon-bench — AXE

**AXE** is the Axon Labs evaluation suite, open-sourced so anyone can benchmark
any model against the same problems we ship our release numbers on.

- **AXE** — the standard suite: general knowledge, coding, and reasoning.
- **AXE-Pro** — the adversarial subset, deliberately outside the easy
  distribution to punish pattern-matching.

Coding tasks are **executed, not eyeballed**: the submitted Python is run
against a hidden test call in a timeout-bounded subprocess, and its output is
compared against the expected result exactly. Text tasks are scored by
whole-token matching after normalisation (case, accents, punctuation stripped)
so a model can't win by substring luck.

## Install

```bash
pip install axon-bench
```

Requires Python 3.9+. Zero dependencies — the client is stdlib only.

## Usage

Point it at any OpenAI-compatible endpoint:

```bash
# OpenAI
axon-bench https://api.openai.com/v1 --model gpt-4o --api-key sk-...

# Local (ollama, vLLM, llama.cpp server, ...)
axon-bench http://localhost:11434/v1 --model llama3.1:8b

# Axon public models
axon-bench https://axon-chat-nu.vercel.app/api/v1 --model axon-1.7 --api-key axk_...
```

```
--track {axe,pro}          which track to run (default: axe)
--pro                      shorthand for --track pro
--category {general,coding,reasoning}
--limit N                  cap the task count per category (smoke tests)
--report PATH              also write the human-readable report to a file
--temperature FLOAT        default 0.0
--max-tokens N             default 2048
--code-timeout SECONDS     per-task execution limit, default 10
--json                     machine-readable output instead of the report
```

Example report:

```
AXE v1 · AXE · 50 tasks · model: your-model
  [1/50] ✓ What is the capital of Australia?
  ...

AXE v1 · AXE · 50 tasks · your-model
===================================
Category      Pass   Score
general      18/20   90.0%
coding       16/20   80.0%
reasoning    13/20   65.0%
--------------------------
Overall      47/60   78.3%

time: total 412.7s · median 6.42s · slowest 19.81s
```

## What's in the bank

170 hand-written tasks, contamination-screened (famous phrasings that leak
the answer are avoided in favour of compositional, slightly-twisted
prompts):

| Track | General | Coding | Reasoning | Total |
|---|---|---|---|---|
| AXE | 46 | 43 | 37 | 126 |
| AXE-Pro | 19 | 13 | 11 | 43 |

Python coding prompts ask for a single function, then run it against a
hidden test call; TypeScript and SQL prompts are construct-checked
(`code_checks`) instead of executed. Every executable task also ships a
reference implementation (`SOLUTIONS`) which the self-check runs to prove
each stored answer is what a correct solution actually returns. AXE-Pro
reuses the same function names with harder contracts (unhashable inputs,
empty inputs, tie-breaking rules) — memorised answers fail, real
implementations pass.

## Python API

```python
from axon_bench import run_bench, select, to_json

tasks = select(category="coding", pro=False)
result = run_bench("http://localhost:11434/v1", "EMPTY", "llama3.1:8b", tasks,
                   track="AXE", temperature=0.0, max_tokens=2048, code_timeout=10)
print(result.category_score("coding"))
```

## Scoring

Scores are percent of tasks passed. Release numbers published on
[axon-chat-nu.vercel.app/benchmarks](https://axon-chat-nu.vercel.app/benchmarks)
are produced with this exact tool.

MIT license · Axon Labs
