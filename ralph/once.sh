#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <plans_dir>"
  echo "  e.g. $0 plans/stage1"
  exit 1
fi

plans_dir=$1

if [ ! -f "$plans_dir/state.json" ]; then
  echo "Error: $plans_dir/state.json not found"
  exit 1
fi

commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")
state=$(cat "$plans_dir/state.json")
prompt=$(sed "s|{{PLANS_DIR}}|$plans_dir|g" ralph/prompt.md)

claude --permission-mode acceptEdits \
  "Previous commits: $commits Current state: $state $prompt"
