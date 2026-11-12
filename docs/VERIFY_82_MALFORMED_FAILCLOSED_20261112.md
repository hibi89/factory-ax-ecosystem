# Factory AX VERIFY — malformed JSON fail-closed QA (2026-11-12 KST)

Scope: First W1 VERIFY product, 82% provisional engineering. Whole Factory AX Ecosystem UNASSESSED. RELEASE HOLD.

## Issue and correction
The owner delivery path previously used top-level JSON object methods before checking its type. Syntactically valid arrays in the owner spec could raise an unhandled AttributeError rather than safely returning BLOCKED, exit code 3. Malformed report receipts, result objects and backup manifests could likewise surface Python exceptions. This is a correctness/security hardening step, not evidence of a real customer exploit.

- factoryax/delivery.py: check top-level approved spec object and root type before path resolution; check receipt sha256 mapping and result object/status/manifests shape.
- factoryax/backup.py: verify that archive metadata sha256 mapping is a dict before indexing.
- tests/test_malformed_rejection.py: four independent CLI-negative cases (spec array, numeric receipt hash map, result array with recomputed unsigned receipt, backup metadata array) demand JSON BLOCKED/exit3, no traceback and no destination output.
- Existing four-role reconciliation, new-only output, source SHA checks, backups and packaging preserved. No customer data or third-party source copied.

## Executed tests
- Targeted: python -m unittest discover -s tests -p test_malformed_rejection.py -v — 4 PASS / 0 FAIL / 0 SKIP.
- Complete suite: python -m unittest discover -s tests -v — 124 PASS / 0 FAIL / 0 SKIP (captured complete verbose log, 34.928 seconds). Initial orchestration wrapper timed out before returning output; diagnostic verbose run completed with Ran 124 tests ... OK.
- python -m compileall -q factoryax scripts tests examples — PASS.
- python scripts/build_candidate.py --output NEW_DIR; repeat with --verify — INTEGRITY_OK, unsigned, RELEASE HOLD, PASS.

## Remaining gates
The default branch already registers manual-only feature-guarded GitHub Actions Windows/Linux QA. At verification time hosted Actions history 0 runs; no connected workflow-dispatch or owner billing-usage tool. Do not execute paid compute without verifying account limits. Native Windows CMD/PowerShell/GUI/NTFS/ACL/Defender, authorized owner acceptance, a true atomic snapshot of four changing sources, upstream PREP/EAI parity, customer data, commercial rights and installer remain UNVERIFIED.

W1 VERIFY stays 82% provisional / 85% NOT ACCEPTED; whole Factory Ecosystem UNASSESSED; RELEASE HOLD. Rollback through prior feature Git commit. No force push or default-branch changes.
