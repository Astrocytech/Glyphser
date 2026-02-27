# Multi-Host Reproducibility Run Checklist

## Preconditions
- Two independent hosts with different OS or CPU family.
- Same git commit checked out.
- Clean repo state on both hosts.
- Fixed dependency lock hash available.

## Host A Steps
1. Verify clean repo and correct commit.
2. Record OS, CPU, Python version.
3. Run: `python3 tools/push_button.py`.
4. Save:
   - `dist/hello-core-bundle.sha256`
   - `conformance/reports/latest.json`
   - `reports/repro/hashes.txt`
5. Record run timestamp.

## Host B Steps
1. Verify clean repo and correct commit.
2. Record OS, CPU, Python version.
3. Run: `python3 tools/push_button.py`.
4. Save:
   - `dist/hello-core-bundle.sha256`
   - `conformance/reports/latest.json`
   - `reports/repro/hashes.txt`
5. Record run timestamp.

## Comparison
1. Compare bundle hashes and conformance report hashes.
2. If mismatch, attach diff of `conformance/reports/latest.json`.
3. Fill `reports/repro/compare-template.md`.
4. Re-run on Host A to rule out drift (same day).

## Exit Criteria
- Hashes match exactly.
- Signed comparison report committed to `reports/repro/`.
