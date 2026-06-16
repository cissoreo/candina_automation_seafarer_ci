@echo off
REM ============================================================
REM Build Seafarer CV Analyzer into a single .exe (Windows)
REM ============================================================

cd /d "%~dp0"
echo Current folder: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Install Python 3.10+ from https://www.python.org/downloads/
    echo During install, CHECK "Add Python to PATH".
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed. See messages above.
    pause
    exit /b 1
)

echo.
echo Building .exe with PyInstaller...
python -m PyInstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "SeafarerCVAnalyzer" ^
    --paths src ^
    --add-data "src;src" ^
    --hidden-import=anthropic ^
    --hidden-import=supabase ^
    --hidden-import=pypdf ^
    --hidden-import=docx ^
    --hidden-import=openpyxl ^
    --hidden-import=cv_extractor ^
    --hidden-import=claude_analyzer ^
    --hidden-import=supabase_manager ^
    --hidden-import=code_mapper ^
    --hidden-import=lookups ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. See messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build complete!
echo Find your .exe at: %CD%\dist\SeafarerCVAnalyzer.exe
echo.
echo IMPORTANT: Copy your .env file into the dist folder
echo (i.e. next to the .exe), then double-click the .exe.
echo ============================================================
pause
