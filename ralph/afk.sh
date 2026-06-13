#!/bin/bash
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <iterations> <plans_dir>"
  echo "  e.g. $0 10 plans/stage1"
  exit 1
fi

iterations=$1
plans_dir=$2

if [ ! -f "$plans_dir/state.json" ]; then
  echo "Error: $plans_dir/state.json not found"
  exit 1
fi

# jq filter to extract streaming text from assistant messages
stream_text='select(.type == "assistant").message.content[]? | select(.type == "text").text // empty | gsub("\n"; "\r\n") | . + "\r\n\n"'

# jq filter to extract final result
final_result='select(.type == "result").result // empty'

echo "=== Ralph AFK started: up to $iterations iterations, plans: $plans_dir ==="

for ((i=1; i<=$iterations; i++)); do
  echo ""
  echo "╔══════════════════════════════════════╗"
  echo "║  ITERATION $i / $iterations"
  echo "╚══════════════════════════════════════╝"

  commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")
  state=$(cat "$plans_dir/state.json")
  prompt=$(sed "s|{{PLANS_DIR}}|$plans_dir|g" ralph/prompt.md)

  echo ">>> Sending prompt to Claude..."

  tmpfile=$(mktemp)

  claude \
    --print \
    --verbose \
    --output-format stream-json \
    --permission-mode acceptEdits \
    "Previous commits: $commits Current state: $state $prompt" \
  | grep --line-buffered '^{' \
  | tee "$tmpfile" \
  | jq --unbuffered -rj "$stream_text"

  echo ""
  echo "--- Iteration $i finished, checking result ---"

  result=$(jq -r "$final_result" "$tmpfile")
  rm -f "$tmpfile"

  if [[ "$result" == *"<promise>NO MORE TASKS</promise>"* ]]; then
    echo ""
    echo "=== Ralph complete after $i iterations ==="
    exit 0
  fi

  echo "--- Moving to next iteration ---"
done

echo ""
echo "=== Ralph finished all $iterations iterations ==="
