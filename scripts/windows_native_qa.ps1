# Synthetic offline QA on an owner-approved Windows 10/11 **ordinary business PC**.
# Only creates new files under a fresh system temp directory; never touches ERP/OT.
# This script and command are not evidence of a Windows PASS unless actually run.
[CmdletBinding()]
param([switch]$GuiSmoke)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ('FactoryAX-QA-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp -ErrorAction Stop | Out-Null
function Check-Exit { if ($LASTEXITCODE -ne 0) { throw "Factory AX native QA failed with exit=$LASTEXITCODE" } }
try {
    Push-Location $repo
    try {
        $python = 'python'
        if (Get-Command 'py' -ErrorAction SilentlyContinue) { $python = 'py' }
        $pyargs = @()
        if ($python -eq 'py') { $pyargs = @('-3') }
        & $python @pyargs -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
        Check-Exit
        & $python @pyargs -m compileall -q factoryax tests scripts examples
        Check-Exit
        & $python @pyargs -m unittest discover -s tests -q
        Check-Exit
        $demo = Join-Path $temp '한글_합성_자료'
        & $python @pyargs (Join-Path $repo 'examples/make_reconcile_synthetic.py') $demo
        Check-Exit
        $report = Join-Path $temp '한글_검수_보고서'
        & $python @pyargs -m factoryax --spec (Join-Path $demo 'approved.json') --output $report
        Check-Exit
        & $python @pyargs -m factoryax --verify-report $report
        Check-Exit
        $archive = Join-Path $temp '합성_백업.zip'
        & $python @pyargs -m factoryax --backup-report $report --output $archive
        Check-Exit
        $restored = Join-Path $temp '한글_복구_보고서'
        & $python @pyargs -m factoryax --restore-backup $archive --output $restored
        Check-Exit
        $candidate = Join-Path $temp '오프라인_후보_패키지'
        & $python @pyargs (Join-Path $repo 'scripts/build_candidate.py') --output $candidate
        Check-Exit
        & $python @pyargs (Join-Path $repo 'scripts/build_candidate.py') --output $candidate --verify
        Check-Exit
        $cmd = Join-Path $candidate 'RUN_VERIFY_WINDOWS.cmd'
        & $cmd --verify-report $restored
        Check-Exit
        if ($GuiSmoke) {
            & $python @pyargs (Join-Path $repo 'scripts/gui_smoke.py')
            Check-Exit
        }
        Write-Output '{"status":"SYNTHETIC_WINDOWS_COMMANDS_PASS","release":"HOLD","note":"Manual real-device acceptance and licensing remain outstanding"}'
    } finally {
        Pop-Location
    }
} finally {
    # Only a fresh QA directory created by this script; no customer files.
    Remove-Item -LiteralPath $temp -Recurse -Force -ErrorAction SilentlyContinue
}
