# Factory AX VERIFY W1 — 82% backup capture safety follow-up

**Date:** 2026-11-12 KST. **Scope:** first-product VERIFY only. Whole Factory AX Ecosystem unassessed, retail release **HOLD**.

## Problem and choice

A backup first called `verify_candidate(report_dir)` then read five files separately. A concurrent writer could modify an already-verified source between verification and ZIP capture, and the function could still return `BACKUP_CREATED`. Although a later restore would reject an inconsistent report, success at the backup stage was incorrect.

- **Option A, full input lock / OS transaction:** would demand native Windows/NTFS locks, ACL and process coordination; brittle for independent reports and would need customer filesystem verification.
- **Option B, fail-closed independent snapshot verification plus after-write verification:** uses source receipts/sha256 and rechecks the report after writing; no extra dependency or network. **Chosen for this engineering iteration**. This is *not* an atomic multi-file snapshot and does not resist a malicious actor replacing a complete valid unsigned receipt.

## Implemented

- Capture the verified source receipt hash before reading.
- Verify exact captured bytes against the receipt, completion digest, source manifest hash and status before creating any backup archive.
- After the ZIP is written and fsynced, verify the live source again; if it drifted or became invalid, fail without returning success.
- Preserve `xb` exclusive create and only clean up a failed archive if its device/inode still matches the file this process created. A competing writer's archive is not removed.
- Add two synthetic concurrency regressions: mutation immediately following first verification, and mutation during ZIP member writes.

## Checked evidence

- Linux Python 3.13.5 (container): `python -m unittest discover -s tests -q` **120 PASS / 0 FAIL / 0 SKIP**.
- `python -m compileall -q factoryax tests scripts examples` **PASS**.
- Local unsigned deterministic candidate `.pyz` build and manifest validation **PASS**.
- Linux Xvfb, real Tk widgets with two synthetic GUI invocations **PASS**.
- No real customer files, external model/API, paid CI, production deployment or main-branch writes.

## Still unverified / acceptance

- GitHub Actions runs **0**; native Windows CMD/PowerShell, Korean filenames on NTFS, junction/ACL/race protections, Defender/installer, actual offline enterprise setup **NOT RUN**.
- Report receipts/ZIP manifests are unsigned; true identity/consent and trusted permissions unverified. No transactional snapshot of 4 moving customer input files or a hostile multi-process filesystem.
- **W1 VERIFY stays 82% provisional; 85% acceptance NOT MET; RELEASE HOLD.** GitHub branch SHA after this code commit must be read from GitHub; previous feature baseline `f687b4affb0f973534734965d98d3d3b70dfd91c`.
- Next: owner-approved Windows 10/11 native check and GitHub CI after account billing/quota and main-branch dispatcher approval, review Windows failures then reassess 85. If permission cannot be obtained, report unverified instead of treating Linux PASS as Windows success.
