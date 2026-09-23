# Changelog

## 1.1.1 — 2026-09-23

### Fixed
- Executable code scoring now compares the hidden call's return value without
  treating unrelated prints in a submission as part of that value.

## 1.1.0 — 2026-09-20

### Added
- Task bank expanded 70 → 170 hand-written, contamination-screened tasks:
  65 general (46 standard / 19 pro), 56 coding (43 / 13), 49 reasoning (38 / 11);
  43 tasks form AXE-Pro.
- New coding coverage: TypeScript and SQL tasks (construct-checked via
  `code_checks`), plus algorithms and data-structure tasks (executed):
  two-pointer 3-sum, edit distance, LCS, islands, BST traversal, RPN
  evaluation, interval merging, trapped water, modular Fibonacci, and more.
- `SOLUTIONS` reference implementations in `axon_bench.tasks`; the
  self-check in test_axe.py runs every executable `test_call` against its
  reference and compares with the stored answer, so expected outputs are
  provably consistent.
- CLI: `--track {axe,pro}` (alias of `--pro`), `--report PATH`, and
  `--limit` now caps per category as documented.
- `render_report` / `write_report` in `axon_bench.runner` (also exported
  from the package): per-category accuracy, overall score, timing stats,
  and a per-task pass/fail table.
- test_axe.py rewritten as a dual-mode suite (pytest or `python
  test_axe.py`): bank integrity, duplicate-prompt detection, select()
  filters, fence extraction (python/typescript/sql/bare), scoring unit
  checks, reference-solution self-check, per-task exception isolation, and
  a mock-server end-to-end run covering the new CLI flags.

### Fixed
- AXE-Pro `dedupe` expected output was the input echoed verbatim;
  duplicates are now actually removed (`[[1, 2], [3], [4]]`).
- `reverse_words` and `title_case` stored unquoted answers, which could
  never match `repr()` of the executed result; both now store the repr.
- Two `aliases` values were bare strings instead of tuples, which
  `text_passed` would have iterated character by character.
- Code-block extraction now recognises ```typescript / ```sql / ```py and
  bare fences (was python-only), with a plain-code fallback for `function`
  / `interface` / SQL prefixes.
- `code_checks` matching is case-insensitive, so lowercase SQL still
  satisfies keyword checks.
- A failing request no longer aborts the run: every task is exception-
  isolated and recorded as a failed result with the error detail.
- Coding tasks with neither `test_call` nor `code_checks` fall back to
  text scoring instead of demanding a code block.

### Changed
- Version 1.1.0 (pyproject, cli, package).
