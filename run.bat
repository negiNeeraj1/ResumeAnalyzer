@echo off
echo ========================================
echo Starting AI Resume Analyzer
echo ========================================
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist venvapp (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the project.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venvapp\Scripts\activate.bat

REM Navigate to App directory
cd App

REM Check if App.py exists
if not exist App.py (
    echo ERROR: App.py not found!
    pause
    exit /b 1
)

REM Copy custom resume_parser.py if not already copied
cd ..
set "VENV_PYRESPARSER=venvapp\Lib\site-packages\pyresparser\resume_parser.py"
set "CUSTOM_PYRESPARSER=pyresparser\resume_parser.py"

if exist "%CUSTOM_PYRESPARSER%" (
    if exist "%VENV_PYRESPARSER%" (
        copy /Y "%CUSTOM_PYRESPARSER%" "%VENV_PYRESPARSER%" >nul 2>&1
    )
)
cd App

echo.
echo Starting Streamlit application...
echo The application will open in your default browser.
echo.
echo Admin credentials:
echo   Username: admin
echo   Password: admin@resume-analyzer
echo.
echo Press Ctrl+C to stop the server.
echo.

streamlit run App.py

pause

