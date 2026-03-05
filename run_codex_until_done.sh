#!/bin/bash

PROMPT_FILE="./run_glyphser_hardening_prompt.txt"

echo "Starting Codex task loop..."

while true
do
    OUTPUT=$(codex exec --full-auto < "$PROMPT_FILE" 2>&1)

    echo "$OUTPUT"

    LAST_LINE=$(echo "$OUTPUT" | tail -n 1)

    # stop when DONE is returned
    if [ "$LAST_LINE" = "DONE" ]; then
        echo "All tasks completed."
        break
    fi

    # stop if usage limit hit
    if echo "$OUTPUT" | grep -q "usage limit"; then
        echo "Codex usage limit reached. Stopping loop."
        break
    fi

    # stop if MCP startup issue
    if echo "$OUTPUT" | grep -q "mcp startup"; then
        echo "MCP startup error detected. Stopping loop."
        break
    fi

    echo "Continuing..."
    sleep 2
done
