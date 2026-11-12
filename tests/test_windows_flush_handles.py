"""Regression: Windows _commit rejects fsync on read-only file handles.

Use a fail-closed simulation on Linux and the real fsync on Windows.  This
checks actual exporter execution, not a source-text substring.
"""
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from factoryax.verify import export_new
from factoryax.delivery import export_candidate, verify_candidate


REPORT = {"manifests": [], "status": "OK", "findings": [], "scope": "synthetic-test"}


class WindowsFlushHandleTests(unittest.TestCase):
    def _run_with_windows_commit_model(self, function, output):
        real_open, real_fsync = Path.open, os.fsync
        recent_mode_by_fd = {}
        synced_regular = []

        def tracked_open(path, mode="r", *args, **kwargs):
            f = real_open(path, mode, *args, **kwargs)
            recent_mode_by_fd[f.fileno()] = mode
            return f

        def require_writable_fsync(fd):
            # Treat directory fd separately on Linux: exporter also fsyncs
            # containing directories for durability where supported.
            if stat.S_ISREG(os.fstat(fd).st_mode):
                mode = recent_mode_by_fd.get(fd)
                if mode == "rb":
                    raise OSError(9, "simulated Windows _commit: read-only handle")
                self.assertTrue(mode and ("+" in mode or mode.startswith(("w", "a", "x"))),
                                f"fsync must use a writable file handle, observed {mode!r}")
                synced_regular.append(mode)
            return real_fsync(fd)

        with patch.object(Path, "open", tracked_open), patch("os.fsync", require_writable_fsync):
            function(REPORT, output)
        self.assertGreaterEqual(len(synced_regular), 3)

    def test_raw_report_export_uses_writable_fsync_handles(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report"
            self._run_with_windows_commit_model(export_new, output)
            self.assertTrue((output / "summary.html").is_file())

    def test_owner_delivery_uses_writable_fsync_handles(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "owner-report"
            self._run_with_windows_commit_model(export_candidate, output)
            self.assertEqual(verify_candidate(output)["status"], "OK")


if __name__ == "__main__":
    unittest.main()
