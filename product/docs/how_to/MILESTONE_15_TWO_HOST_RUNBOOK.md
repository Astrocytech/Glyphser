# Milestone 15 Two-Host Runbook (Local Network)

Goal: Run the full push-button pipeline on two **independent** hosts that differ by OS or CPU family, compare hashes, and produce a signed comparison report.

## A. Requirements

### Hardware/OS
- Two machines on the same local network.
- Hosts must differ by OS **or** CPU family.
  - Example: Host A Ubuntu + Host B Debian, or Host A x86_64 + Host B arm64.

### Software (Both Hosts)
- `python3` (3.10+ recommended; 3.12 used in the project).
- `git`
- `pip` (for Python packages)

### Repo State (Both Hosts)
- Same commit checked out.
- Clean working tree (no uncommitted changes).
- `requirements.lock` present and identical.

## B. One-Time Setup (Both Hosts)

1. Install git + python3 + pip
   - Example (Debian/Ubuntu):
     - `sudo apt update`
     - `sudo apt install -y git python3 python3-pip`

2. Clone the repo on each host
   - `git clone <REPO_URL> Glyphser`
   - `cd Glyphser`

3. Checkout the exact same commit on both hosts
   - `git checkout <COMMIT_SHA>`

4. Verify repo clean state
   - `git status -s` (must be empty)

5. Confirm Python version
   - `python3 --version`

6. Install dependencies
   - `python3 -m pip install -r requirements.lock`

7. Verify dependency lock hash
   - `sha256sum requirements.lock`
   - Compare to `evidence/repro/dependency-lock.sha256` in the repo.

## C. Capture Host Metadata (Both Hosts)

1. Run the host metadata helper:
   - `python3 scripts/repro/host_meta.py`
2. Save output for the comparison report.

## D. Run the Pipeline (Both Hosts)

1. Run the full pipeline:
   - `python3 tooling/push_button.py`
2. Collect the following artifacts:
   - `artifacts/bundles/hello-core-bundle.sha256`
   - `evidence/conformance/reports/latest.json`
   - `evidence/repro/hashes.txt`

## E. Compare Results

1. Compare `artifacts/bundles/hello-core-bundle.sha256` between Host A and Host B.
2. Compare hash of `evidence/conformance/reports/latest.json` between hosts:
   - `sha256sum evidence/conformance/reports/latest.json`
3. Compare `evidence/repro/hashes.txt` between hosts.

If any mismatch occurs:
- Attach a diff of `evidence/conformance/reports/latest.json` to the report.

## F. Third Verification Run (Host A)

1. Re-run `python3 tooling/push_button.py` on Host A.
2. Ensure all hashes match Host A’s first run.

## G. Fill the Comparison Report

1. Copy `evidence/repro/compare-template.md` to a new file:
   - Example: `evidence/repro/compare-YYYYMMDD.md`
2. Fill in:
   - Host metadata
   - Hashes from both hosts
   - Outcome and notes

## H. Sign and Commit

1. Add a signature line in the report (manual signature or PGP if desired).
2. Commit the report into `evidence/repro/`.

## I. Milestone 15 Completion Criteria

- Hashes match exactly across hosts.
- Signed comparison report committed.
- Third Host A verification run confirms no drift.

## Troubleshooting

- If pipeline fails, re-run with a clean repo and confirm dependencies.
- If hashes differ, compare conformance report JSON and check host metadata.
- If still mismatching, pause Milestone 15 and investigate nondeterminism.
