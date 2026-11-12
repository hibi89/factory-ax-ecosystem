"""Portable safety/contract tests for owner-only Windows QA entrypoint."""
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'scripts'))
import owner_windows_qa as qa

class WindowsOneClickContractTest(unittest.TestCase):
    def test_plan_exposes_all_native_gates(self):
        p=subprocess.run([sys.executable,str(BASE/'scripts/owner_windows_qa.py'),'--plan'],
                         capture_output=True,text=True,check=True)
        obj=json.loads(p.stdout)
        self.assertEqual(obj['release'],'HOLD')
        self.assertIn('native_cmd_blocked',obj['steps'])
        self.assertIn('native_tk_gui',obj['steps'])
        self.assertIn('original_input_unchanged',obj['steps'])

    def test_runner_refuses_claiming_windows_pass_on_linux(self):
        with patch.object(qa.os,'name','posix'):
            result,summary=qa.native_qa()
        self.assertEqual(result,3)
        self.assertEqual(summary['status'],'BLOCKED')
        self.assertEqual(summary['reason'],'NATIVE_WINDOWS_REQUIRED')

    def test_manifest_absent_or_malformed_is_fail_closed(self):
        with patch.object(qa,'SOURCE_MANIFEST',BASE/'tests/absent-qa-source-manifest.json'):
            with self.assertRaises(OSError):
                qa.verify_source_bundle()

    def test_launcher_uses_separate_exit_code_lines_and_no_powershell_policy_bypass(self):
        script=(BASE/'RUN_FACTORYAX_WINDOWS_QA.cmd').read_bytes().decode('ascii')
        self.assertIn('set "qa_result=%errorlevel%"',script)
        self.assertIn('exit /b %qa_result%',script)
        self.assertNotIn('ExecutionPolicy',script)
        self.assertNotIn('powershell',script.lower())
        self.assertIn('pause',script)

if __name__=='__main__':
    unittest.main()
