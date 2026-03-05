#!/bin/bash

PROMPT_FILE="./run_glyphser_hardening_prompt.txt"

echo "Starting Codex task loop..."

while true
do
    PROMPT=$(cat "$PROMPT_FILE")

    OUTPUT=$(timeout -k 5 900 codex exec --full-auto "$PROMPT" 2>&1)

    echo "$OUTPUT"

    LAST_LINE=$(echo "$OUTPUT" | tail -n 1)

    if [ "$LAST_LINE" = "DONE" ]; then
        echo "All tasks completed."
        break
    fi

    if echo "$OUTPUT" | grep -qi "usage limit"; then
        echo "Usage limit reached. Stopping."
        break
    fi

    if echo "$OUTPUT" | grep -qi "mcp startup"; then
        echo "MCP startup error. Restarting Codex..."
        sleep 5
        continue
    fi

    echo "Continuing..."
    sleep 3
done
