#!/bin/bash

PROMPT_FILE="./run_glyphser_hardening_prompt.txt"

echo "Starting Codex task loop..."

ITER=1

while true
do
    echo ""
    echo "----------------------------------------"
    echo "Starting Codex iteration $ITER"
    echo "Time: $(date)"
    echo "----------------------------------------"

    PROMPT=$(cat "$PROMPT_FILE")

    OUTPUT=$(timeout -k 5 900 codex exec --full-auto "$PROMPT" 2>&1)

    echo "$OUTPUT"

    LAST_LINE=$(echo "$OUTPUT" | tail -n 1)

    if [ "$LAST_LINE" = "DONE" ]; then
        echo "All tasks completed."
        break
    fi

    if echo "$OUTPUT" | grep -qi "usage limit"; then
        echo "Usage limit reached."
        break
    fi

    if echo "$OUTPUT" | grep -qi "mcp startup"; then
        echo "MCP startup error detected — restarting agent..."
        sleep 5
        ITER=$((ITER+1))
        continue
    fi

    echo "Iteration finished, restarting Codex..."
    sleep 3
    ITER=$((ITER+1))
done
