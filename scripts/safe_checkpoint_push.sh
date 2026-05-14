#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This folder is not a git repository yet. Run git init and add a private GitHub remote first."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "No origin remote configured. Add your private GitHub repository as origin first."
  exit 1
fi

echo "Running validation before checkpoint push..."
python3 -m unittest discover -s tests -p "test_*.py"
PYTHONPYCACHEPREFIX=/tmp/nudge_engine_pycache python3 -m compileall src tests

python3 scripts/generate_change_summary.py \
  --test-status "tests_passed" \
  --note "Safe checkpoint generated before push."

git add .

if git diff --cached --quiet; then
  echo "No changes to commit."
else
  COMMIT_MESSAGE="${1:-safe checkpoint: validated nudge engine update}"
  git commit -m "$COMMIT_MESSAGE"
fi

git push origin HEAD
