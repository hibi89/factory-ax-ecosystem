# First hosted Windows CI failure: actual GitHub run 43173438702

- At UTC 2026-11-12 07:11:34, owner ran `workflow_dispatch` manually against `feature/data-verify`, SHA `17142a9247c2b787a7881d23fa048470716b63b1`.
- Run: https://github.com/hibi89/factory-ax-ecosystem/actions/runs/43173438702, conclusion `failure`.
- Ubuntu job `131031951602`: SUCCESS. Full 134/134 isolated Python unittest; compile; artifact build + verify; synthetic four-role CLI OK; receipt/report/backup/restore OK; real Tk widgets via Xvfb synthetic PASS.
- Windows job `131031952079`: FAILURE, **Windows Server 2025**, hosted Python **3.11.9**. Python compile passed. Step `Isolated synthetic regression` returned exit1 after discovering 15 `test_backup.py` cases. Original subprocess wrapper hid failure stdout/stderr, so exact error cause **not established**. All later Windows steps were skipped.
- Diagnostic improvement: print at most 20k characters of failing synthetic stderr/stdout, with ASCII escaping; exit remains 1, no false PASS, no private/user files run. Local Linux `test_backup.py` 15/15 PASS and simulated failure-path log assertions PASS. No new hosted Windows run yet.
- Required next run: **new** Run workflow selecting `feature/data-verify` AFTER this fix's commit. Do not use `Re-run jobs` from old SHA because it will execute original log-suppressing source again. Account private Windows Actions usage/remaining budget still owner-controlled. Customer physical Windows machine remains untested.
- W1 VERIFY 82% provisional, 85 unaccepted, whole Factory AX ecosystem UNASSESSED, RELEASE HOLD.
