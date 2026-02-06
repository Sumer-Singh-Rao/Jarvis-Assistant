@echo off
cd /d "%~dp0"
echo ================================================
echo Starting JARVIS AI Assistant
echo ================================================
echo.
python -u jarvis_frontend.py
echo.
echo ================================================
if errorlevel 1 (
    echo ERROR: Program exited with error
) else (
    echo Program closed normally
)
echo ================================================
pause
