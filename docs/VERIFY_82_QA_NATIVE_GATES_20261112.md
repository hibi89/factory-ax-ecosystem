# Factory AX VERIFY 85-target native-readiness increment — 2026-11-12 KST

**Verified checkpoint: 82% provisional engineering, 85 NOT ACCEPTED; RELEASE HOLD.** The percentage describes only first product W1 VERIFY, not the Factory AX Ecosystem. The prior exact source baseline is `feature/data-verify@06a64f9c84aef37661423ec6dde49c2c12359b65`. Existing `main`, all source datasets and unrelated product repos are unchanged.

## Work performed

1. **Fix a concrete unsafe competing-backup race.** Previous `backup()` used `open('xb')` but then unconditionally unlinked the target on error: if another process created the ZIP between preflight and exclusive open, the failure handler could delete **their existing file**. New code tracks the created file's device/inode and only cleans a matching file created by this invocation. Unknown/replaced identity => leave the path alone. Added two negative tests: competing writer remains byte-for-byte unchanged; failed write cleans only own incomplete archive.
2. **Real Linux GUI path with display, not only source import.** Added `scripts/gui_smoke.py`; launched actual Tk widgets under Xvfb, supplied invented approved four-role source, invoked review button twice and verified first OK then no-overwrite BLOCKED, with unchanged input SHA. Fixed canceled folder chooser previously constructing `/FactoryAX-New-Report`; cancel now preserves empty selection. Cleared old success text when a later operation is blocked, and corrected UI status.
3. **Native Windows owner QA procedure** `scripts/windows_native_qa.ps1`: local Python >=3.11 check, compile, complete synthetic unittest, invented four-role output, verification, backup, restore, deterministic zipapp/CMD and Korean paths in a fresh `%TEMP%` directory, opt-in GUI smoke. Must run by an authorized Windows owner; script does not claim it has run. It does NOT connect to ERP/OT, enable a network service, install a driver or delete customer files.
4. **Manual-only CI readiness:** extended the existing `workflow_dispatch` matrix to include four-role CLI/receipt/backup/restore on Ubuntu+Windows and Xvfb real Tk synthetic smoke on Linux. No Actions run dispatched; GitHub private runner minutes/cost approval is not established.

## Actual verification evidence at this development checkpoint

| Item | Result | Environment/limits |
|---|---|---|
| `python -m unittest discover -s tests -q` | **117 PASS / 0 FAIL / 0 SKIP** | Local Linux Python3.13.5, synthetic; previous 115 preserved +2 backup race tests |
| `xvfb-run -a python scripts/gui_smoke.py` | **PASS** (real Tk screen, button invocations 2, 0 source changes) | Linux Xvfb; not Windows native |
| `python -m compileall -q factoryax tests scripts examples` | **PASS** | Python3.13.5 only |
| Four-role synthetic CLI report→verify→backup→restore→verify | **PASS** | Linux tempfile only, no customer or OT files |
| `python scripts/build_candidate.py --output NEW` and `--verify` | **PASS** | Unsigned deterministic source-only .pyz/CMD; local Linux build |
| GitHub Actions Ubuntu/Windows runs | **NOT RUN** | Manual-only; no unapproved private Actions consumption |
| Windows 10/11 native `.cmd`/Tkinter/PowerShell/NTFS/reparse/Defender/SmartScreen | **NOT RUN** | Runner/device not available in current work environment |
| Customer business acceptance/actual API/model/external source rights | **NOT RUN** | W1 retail release remains HOLD |

### Remaining 85% acceptance blockers

- Run exact committed code on authorized Windows 10/11 and validate the console/GUI, Korean path/CSV/Excel behavior, NTFS reparse/junction and file permissions, concurrent paths, backup and restore, network refusal and desktop/Defender experience. The owner-only native QA script is a test aid, not a passed test.
- Execute authorized **clean GitHub Windows+Linux workflow** on this source SHA and inspect job logs; do not silently spend private Actions minutes. Hosted Windows CI is not a substitute for the physical acceptance at 95%.
- A cross-file atomic snapshot of the four manufacturing source files and real authenticated human approval are not implemented. The system reads sources sequentially with SHA recheck, and receipt is **UNSIGNED**. Do not claim complete integrity vs concurrent hostile writers.
- Confirm explicit third-party redistribution license, notices, customer documents/consent, and actual Windows packaging support. Windows `.cmd` currently needs externally installed Python3.11+ and is not a signed EXE or installer.

**Scoring decision:** No new 3%p granted merely for tests or scripts. Preserve W1 **82% provisional**, mark 85 target `BLOCKED_BY_NATIVE_VALIDATION` until Windows+CI evidence is observed. Full Factory AX Ecosystem final completion `UNASSESSED`, all sale/Production RELEASE HOLD.

**Rollback:** Original feature exact commit `06a64f9c84aef37661423ec6dde49c2c12359b65` plus Git history; no force-push or merge. Main baseline `29b9653ccbc4bcd36a190f9e9d78954bcc4dae76` is unchanged.
