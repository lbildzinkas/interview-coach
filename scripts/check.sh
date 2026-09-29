#!/usr/bin/env bash
# One command that runs every check, locally and in CI (same command everywhere).
# Tool docs: ruff https://docs.astral.sh/ruff/ | pyright https://microsoft.github.io/pyright/
#            pytest https://docs.pytest.org/
# Run it after `uv sync` (see README.md).
set -euo pipefail

echo "== ruff check (lint) =="
uv run ruff check .

echo "== ruff format --check (formatting) =="
uv run ruff format --check .

echo "== pyright (type check) =="
uv run pyright

echo "== pytest (tests) =="
uv run pytest
