#!/usr/bin/env bash
set -euo pipefail
python tooling/security/security_workflow_wrapper.py --workflow release -- "$@"
