"""Run Factory AX synthetic unittest suites in isolated processes.

Avoid prior cross-module latency/side-effects by launching each test_*.py separately.
No dependencies, network requests, customer data or environment modifications.
Return a non-zero result for missing/failed/timed-out/zero-test suites.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
RESULT_RE = re.compile(r"\bRan\s+(\d+)\s+tests?\s+in\s+")


def run_suites(*, timeout: int = 65) -> tuple[int, dict]:
    patterns = sorted(p.name for p in TESTS.glob("test_*.py") if p.is_file())
    report: dict = {"schema": "factoryax.ci-regression.v1", "status": "FAIL",
                    "total_passed": 0, "suites": []}
    if not patterns:
        report["reason"] = "NO_TEST_SUITES"
        return 2, report
    for pattern in patterns:
        entry = {"suite": pattern, "status": "FAIL"}
        report["suites"].append(entry)
        argv = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-q"]
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            entry["reason"] = "TIMEOUT"
            return 3, report
        except OSError:
            entry["reason"] = "SPAWN_FAILED"
            return 3, report
        output = result.stdout + "\n" + result.stderr
        match = RESULT_RE.search(output)
        count = int(match.group(1)) if match else 0
        if result.returncode != 0 or count < 1 or "FAILED (" in output or "OK (skipped=" in output:
            entry["reason"] = "NONPASS_OR_ZERO_TESTS"
            entry["exit_code"] = result.returncode
            entry["discovered"] = count
            # Windows failure #43173438702 discovered 15 tests but swallowed
            # their stderr. Print bounded ASCII-safe diagnostics without
            # changing failure behavior. Synthetic suites only, no user files.
            safe = output[-20000:].encode("ascii", "backslashreplace").decode("ascii")
            print("FAILED_SUITE_DIAGNOSTICS_START " + pattern, file=sys.stderr, flush=True)
            print(safe, file=sys.stderr, flush=True)
            print("FAILED_SUITE_DIAGNOSTICS_END " + pattern, file=sys.stderr, flush=True)
            return 1, report
        entry.update({"status": "PASS", "tests": count})
        report["total_passed"] += count
    report["status"] = "PASS"
    return 0, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Factory AX synthetic CI per-file unittest isolation")
    parser.add_argument("--timeout", type=int, default=65, help="Maximum seconds per test file")
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.timeout > 180:
        parser.error("timeout must be within 1..180 seconds")
    code, report = run_suites(timeout=args.timeout)
    print(json.dumps(report, sort_keys=True, ensure_ascii=False), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
