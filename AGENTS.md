# Repository Guidelines

## Project Structure

- `worklog_summarizer.py`: main entry point; collects Markdown worklogs and (optionally) calls Claude via CLI.
- `config.py.example`: configuration template; copy to `config.py` for local use (never commit it).
- `claude_analysis_prompt.md`: prompt used for Claude analysis.
- `run_summary.sh`: interactive helper script for local runs.
- `weekly_cron.sh`, `crontab_example.txt`, `README_CRON.md`: cron automation to generate and push weekly reports.
- `claude_input/`, `worklog_summary/`: generated outputs (git-ignored).
- `experiment/`: cron/Claude invocation test scripts and notes.

## Build, Test, and Development Commands

This repo is intentionally “no-deps” (Python stdlib only).

- `cp config.py.example config.py`: create your local config and set `WORKLOG_PATH` (and `CLAUDE_PATH` if needed).
- `python3 worklog_summarizer.py`: generate a 7-day report using config defaults.
- `python3 worklog_summarizer.py 14`: generate a report for the last 14 days.
- `python3 worklog_summarizer.py 7 --no-claude`: collect logs and write outputs without calling Claude (safe for local testing).
- `./run_summary.sh`: interactive wrapper around `worklog_summarizer.py`.
- `./weekly_cron.sh`: generate a 7-day report and push to RocketChat (requires external `push_to_rocketchat` script).

## Coding Style & Naming Conventions

- Python: 4-space indentation, type hints where practical, keep UTF-8 + existing (often Chinese) docstrings consistent.
- Shell: POSIX-ish `bash`, keep `set -e`, quote variables, prefer absolute paths in cron-facing scripts.
- Generated files: keep outputs under `claude_input/` and `worklog_summary/` and do not commit them.

## Testing Guidelines

There is no formal unit test suite. Use these smoke checks:

- Minimal run: `python3 worklog_summarizer.py 1 --no-claude`
- Cron-like env: `./experiment/test_cron_simple.sh` (simulates reduced `PATH`)

If you add tests, place them under `experiment/` and keep them runnable without network access.

## Commit & Pull Request Guidelines

- Commits in history are short and often descriptive (some use Conventional Commits like `feat:`). Prefer `feat: ...`, `fix: ...`, or a concise imperative subject.
- PRs should include: what changed, how to verify (commands), and any config/cron impact. Never include secrets or machine-specific paths; keep `config.py` local-only.

## Security & Configuration Notes

- `config.py` may contain sensitive paths and tool locations; it is git-ignored by design. Prefer environment variables for anything credential-like.
- Claude calls require a working `claude` CLI; cron environments often need an explicit `CLAUDE_PATH` (see `experiment/TEST_CRON.md`).
