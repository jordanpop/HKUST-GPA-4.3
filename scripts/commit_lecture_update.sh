#!/usr/bin/env bash
# Commit + push only the lecture-update files. Avoids the repo's
# common dirty-state noise (.DS_Store, stale drafts, deleted input PDFs).
#
# Usage:
#   scripts/commit_lecture_update.sh <code> "<commit message>"
#
# Example:
#   scripts/commit_lecture_update.sh 3040 "L7+L8: regenerate Neuro notes"
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <code> \"<commit message>\""
  exit 2
fi

CODE="$1"
MSG="$2"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Unstage everything, then stage only the canonical lecture-update files.
git reset HEAD -- . >/dev/null

FILES=("${CODE}.html" "data/${CODE}.json")
[[ -f CLAUDE.md ]] && git diff --quiet CLAUDE.md || FILES+=("CLAUDE.md")

git add "${FILES[@]}"

if git diff --cached --quiet; then
  echo "Nothing staged for ${CODE}. Aborting."
  exit 1
fi

git commit -m "$MSG"
git push
