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

Options:

```
--pro                      run the adversarial AXE-Pro subset
--category {general,coding,reasoning}
--limit N                  cap the task count (good for quick smoke tests)
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

============================================
AXE results — your-model
============================================
  General      72.0
  Coding       80.0
  Reasoning    65.0
--------------------------------------------
  Overall      72.3
```

## What's in the bank

70 hand-written tasks, contamination-screened:

| Track | General | Coding | Reasoning |
|---|---|---|---|
| AXE | 20 | 15 | 15 |
| AXE-Pro | 10 | 5 | 5 |

Coding prompts ask for a single function only, then run it. AXE-Pro reuses the
same function names with harder contracts (unhashable inputs, empty inputs,
tie-breaking rules) — memorised answers fail, real implementations pass.

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
