# Factory AX VERIFY W1-82 — path ancestor QA, 2026-11-12 KST

**Scope:** first-product W1 VERIFY 82% provisional only; **85% not accepted**, whole Factory AX Ecosystem UNASSESSED, all RELEASE HOLD. Existing source baseline: `7ac39e8009e3c2312e1f2b616ec66f0d1d237794`.

## Verified security improvement
Previous report/output creation, verification and backup/restore checks looked at only the leaf or immediate parent. An ancestor symbolic link or Windows junction could alias the intended path to an unintended directory. New `_require_plain_directory` in `factoryax/delivery.py` checks **every existing directory component** with `lstat` and rejects symlinks, non-directories and Windows reparse attributes; applies to local spec parent, approved source root, report creation/verification, backup source/destination and restore source/destination. No customer files or original repos were changed.

**Design comparison:** (A) `Path.resolve()` alone, minimal maintenance but silently follows symlinks/junctions; (B) component-wise `lstat` fail-closed, more metadata calls but explicit boundary. Selected B for limited offline W1. This is a **preflight only**, not race-free handle-level isolation; Windows NTFS/ACL/junction and concurrent directory replacement remain unverified.

Six added negative tests cover: report create via symlinked ancestor, report verification via alias, spec intake via alias, backup destination alias, restore destination alias, backup ZIP source alias. Tests verify no redirected outputs were created, and existing reports remain usable. On systems without symlink privileges these tests may skip; Linux executed all six without skips.

## Actual executed QA, Linux Python3.13, entirely synthetic
| Test module | Completed |
|---|---:|
| `test_backup` | 15 PASS |
| `test_delivery` | 24 PASS |
| `test_malformed_rejection` | 4 PASS |
| `test_profile_contract` | 4 PASS |
| `test_reconciliation` | 29 PASS |
| `test_verify` | 54 PASS |
| **Total, six isolated module runs** | **130 PASS / 0 FAIL / 0 SKIP** |

Each module was run as `PYTHONPATH=tests python -m unittest -q <module>`. Two **whole-suite invocations timed out** without result; these are not counted as passing. The six individually completed module runs collectively cover the test files. `python -m compileall -q factoryax tests scripts examples` PASS.

Independent unsigned packaged `.pyz` generated and checked by `scripts/build_candidate.py --output NEW_DIR` and `--verify`: PASS. Fresh ZIPAPP synthetic four-source CLI `--spec` -> `--verify-report` -> `--backup-report` -> `--restore-backup` -> `--verify-report`: PASS. Linux `xvfb-run -a python scripts/gui_smoke.py`: PASS, Tk widgets 2 button invocations, inputs unchanged.

## Remaining gates
At inspection, GitHub Actions run history for Factory was **0**; manual Windows/Linux CI workflow registered on main+feature but **not dispatched**; connector has no dispatch/billing access. **Native Windows CMD/PowerShell/Tkinter/NTFS junction/ACL/Korean, Defender/SmartScreen, production installer and actual customer data are NOT TESTED.** Synthetic unsigned hash receipts are not authentic approvals. The four-source ingest is sequential, not atomic multi-file transaction. No Windows or commercial success claim.

Next: owner confirms personal account Actions remaining included usage and spend stop, dispatches manual `feature/data-verify` run from Actions tab, or executes reviewed local Windows QA; read exact Windows/Linux evidence and reevaluate 85 only after formal matrix. Roll back to prior `7ac39e8009e3c2312e1f2b616ec66f0d1d237794` via normal revert if needed; no force, no main/other-source modification. **VERIFY 82% provisional, 85 NOT ACCEPTED, RELEASE HOLD.**
