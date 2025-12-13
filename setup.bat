@echo off
echo ========================================
echo AI Resume Analyzer - Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9.12 from https://www.python.org/downloads/release/python-3912/
    pause
    exit /b 1
)

echo [1/6] Python found!
python --version
echo.

REM Navigate to project directory
cd /d "%~dp0"
echo [2/6] Current directory: %CD%
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if exist venvapp (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venvapp
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)
echo.

REM Activate virtual environment
echo [4/6] Activating virtual environment...
call venvapp\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Navigate to App directory
cd App
echo [5/6] Installing Python packages from requirements.txt...
echo This may take several minutes...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)
echo.
echo Packages installed successfully!
echo.

REM Download spacy model
echo [6/6] Downloading spaCy English model...
python -m spacy download en_core_web_sm
if errorlevel 1 (
    echo WARNING: Failed to download spaCy model. You may need to run this manually.
    echo Run: python -m spacy download en_core_web_sm
)
echo.

REM Copy custom resume_parser.py
echo [EXTRA] Copying custom resume_parser.py...
cd ..
set "VENV_PYRESPARSER=venvapp\Lib\site-packages\pyresparser\resume_parser.py"
set "CUSTOM_PYRESPARSER=pyresparser\resume_parser.py"

if exist "%CUSTOM_PYRESPARSER%" (
    if exist "%VENV_PYRESPARSER%" (
        copy /Y "%CUSTOM_PYRESPARSER%" "%VENV_PYRESPARSER%"
        echo Custom resume_parser.py copied successfully!
    ) else (
        echo WARNING: Could not find venv pyresparser folder. This will be done after first pip install.
    )
) else (
    echo WARNING: Custom resume_parser.py not found in pyresparser folder!
)
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo IMPORTANT NEXT STEPS:
echo 1. Make sure MySQL is installed and running
echo 2. Create a database named 'cv' in MySQL:
echo    - Option A: Run create_database.bat (interactive)
echo    - Option B: Run: mysql -u root -p ^< database_setup.sql
echo    - Option C: Manually create database 'cv' in MySQL
echo 3. Update database credentials in App\App.py if needed
echo    (Default: host='localhost', user='root', password='root@MySQL4admin')
echo 4. Run the application using: run.bat
echo    (Tables will be created automatically on first run)
echo.
pause

