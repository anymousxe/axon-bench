# axon-bench — AXE

AXE is an open evaluation suite for OpenAI-compatible chat endpoints. Release
**1.1.1** now carries task revision **2026-09-23-depth-1**. The package release
and task revision are separate identifiers: old 1.1.1 task-bank results are not
comparable with this revision.

| Independent track | General | Coding | Reasoning | Total |
|---|---:|---:|---:|---:|
| AXE | 48 | 48 | 47 | 143 |
| AXE-Pro | 48 | 48 | 47 | 143 |

The 286 prompts are disjoint. Pro is a separate, harder track, not the same
questions with renamed inputs. Each task has a stable ID, category, difficulty
(`easy`, `medium`, `hard`, `expert`), answer key, and reference/derivation.
Difficulty labels are editorial assessments, not empirically calibrated levels.
General tasks mix stable domain knowledge, interpretation, and source-bound
mini-policies. Reasoning includes multi-step constraints, probability,
combinatorics, optimization, and explicit finite systems. No contamination-free
or independently source-audited claim is made.

## Install and run

Python 3.9+ and a POSIX system with Python's `resource` module are required for
executable coding scoring. The client and grader use only the standard library.
Install the checked-out revision with `pip install .`; pin the source commit and
record the task hash for reproducibility. An old `v1.1.1` tag alone does not
identify this revised bank.

```bash
axon-bench http://localhost:11434/v1 --model my-model --json
axon-bench https://example.com/v1 --model my-model --api-key TOKEN --track pro
axon-bench URL --model NAME --category coding --difficulty hard --limit 5
axon-bench URL --model NAME --report run.txt --json
```

| Option | Meaning |
|---|---|
| `--track {axe,pro}` | Independent track; default `axe` |
| `--pro` | Shorthand for `--track pro` |
| `--category {general,coding,reasoning}` | Category filter |
| `--difficulty {easy,medium,hard,expert}` | Difficulty filter |
| `--limit N` | At most N tasks **per selected category**; partial run only |
| `--temperature FLOAT` | Default 0.0 |
| `--max-tokens N` | Default 2048; record when comparing runs |
| `--code-timeout SECONDS` | Wall-clock limit per coding submission; default 10 |
| `--reasoning-effort LEVEL` | Optional provider reasoning setting; omitted by default |
| `--enhancement` / `--no-enhancement` | Optional Axon enhancement setting; omitted by default |
| `--report PATH` | Also write a readable report |
| `--json` | Machine-readable results with raw responses |

The current Axon comparison uses temperature `0`, `4096` output tokens,
reasoning `none`, enhancement enabled, and a `3`-second code timeout:

```bash
axon-bench https://axon-api.anymousxe-info.workers.dev/v1 --model axon-1.8-pro --api-key TOKEN --temperature 0 --max-tokens 4096 --reasoning-effort none --enhancement --code-timeout 3 --track axe --json
```

Repeat with `--track pro` for the other 143 questions.

## Scoring and execution

Knowledge scoring compares the whole answer with the key or an explicit alias.
Reasoning scoring also accepts a clearly selected final answer after a worked
explanation: a final-answer label, terminal boxed/emphasized answer, or a
standalone scalar following the derivation. Extraction never consults the key.
Candidate lists without a selected answer, negations, and answers containing
alternatives do not pass. Case, whitespace and simple presentation wrappers are
normalized; signs, decimal points and accents retain meaning. JSON records
scorer revision `2026-09-23-final-answer-2` separately from the task hash.

All 96 coding tasks require Python functions. Each submission is executed
against at least four cases, including boundaries and nontrivial inputs; all
must pass. Cases and expected values are in the public source but are **not
sent to the model**. The reference implementations are separately authored
from the literal expected values. Comparisons preserve collection types and
boolean meaning while ignoring dictionary insertion order and equivalent
integer/float representation. Debug prints do not affect the return value.
Construct-only TypeScript/SQL items were removed: a keyword is not execution.

The subprocess uses a temporary working directory, an empty environment,
isolated Python initialization, CPU/address-space/file-size/file-descriptor
limits, bounded captured output, and process-group cleanup. These controls
reduce accidental resource exhaustion; **they are not an OS security sandbox**.
Submitted Python can still access host resources allowed to its user. Run the
benchmark in an externally isolated, disposable container or VM, without
credentials or sensitive mounted files, when executing untrusted model code.

Scores are `100 * passed / total`. Refusals, wrong answers, invalid code
and timeouts fail. HTTP/transport
and unexpected grader failures are separately marked `error`, set
`publishable: false`, and cause a nonzero CLI exit. Although raw totals retain
these failed rows, **do not publish rankings from an error-contaminated run**.
A successful partial run is not a full-track result; confirm IDs and counts.

## Python API

```python
from axon_bench import select_tasks, run_bench, to_json, TASK_REVISION, TASK_HASH

tasks = select_tasks(pro=True, category="coding")
result = run_bench("http://localhost:11434/v1", "EMPTY", "my-model", tasks,
                   track="AXE-Pro", temperature=0, max_tokens=2048,
                   code_timeout=10)
print(to_json(result))
```

The existing `select(...)`, `Task`, `TASKS`, `GENERAL`, `CODING`, `REASONING`,
`SOLUTIONS`, `score_task(...)`, and report APIs remain available in their
original modules. New Task fields have defaults for existing callers.
`SOLUTIONS[task.solution_name]` retrieves each executable reference.

JSON records package version, task revision, SHA-256 of the canonical complete
bank (including cases and reference implementations), settings, category and
difficulty totals, request-error count, and per-task ID/prompt/category/track/
difficulty/response/pass/detail/timing. Retain the source commit, run date,
model ID, enhancement setting if applicable, all settings and raw responses.
The hash identifies the bank, not stochastic model behavior. Compare models
only on the same task revision/hash and selection; do not merge historical
results from the previous 127/43 bank.

## Offline verification

```bash
python test_axe.py
# or: pytest test_axe.py
```

Verification exercises all 96 reference implementations against stored cases,
strict answer regressions, candidate dumps, signed values, boundary-case
failures, resource timeout, request-error isolation and a local HTTP CLI run.
Reference agreement checks implementation/key consistency, not independent
proof of every domain fact or reasoning derivation. The individual references
are included to support that review.

MIT license · Axon Labs
