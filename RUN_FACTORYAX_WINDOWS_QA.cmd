@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto python_fallback
py -3 "%~dp0scripts\owner_windows_qa.py"
set "qa_result=%errorlevel%"
goto finished
:python_fallback
python "%~dp0scripts\owner_windows_qa.py"
set "qa_result=%errorlevel%"
:finished
echo.
if not "%qa_result%"=="0" echo Factory AX Windows QA FAILED or BLOCKED, status=%qa_result%
if "%qa_result%"=="0" echo Factory AX SYNTHETIC WINDOWS QA PASS. RELEASE remains HOLD.
echo Review RESULT_FILE printed above. Share only that JSON file after reviewing it.
pause
exit /b %qa_result%
