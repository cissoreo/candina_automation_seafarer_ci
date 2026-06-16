#!/bin/bash

# ============================================================
# Build Seafarer CV Analyzer into a single executable (macOS)
# ============================================================

cd "$(dirname "$0")"

echo "Current folder: $(pwd)"
echo

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed."
    echo "Install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

echo "Python version:"
python3 --version
echo

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Dependency installation failed. See messages above."
    exit 1
fi

echo
echo "Building executable with PyInstaller..."

python3 -m PyInstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "SeafarerCVAnalyzer" \
    --paths src \
    --add-data "src:src" \
    --hidden-import=anthropic \
    --hidden-import=supabase \
    --hidden-import=pypdf \
    --hidden-import=docx \
    --hidden-import=openpyxl \
    --hidden-import=cv_extractor \
    --hidden-import=claude_analyzer \
    --hidden-import=supabase_manager \
    --hidden-import=code_mapper \
    --hidden-import=lookups \
    main.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed. See messages above."
    exit 1
fi

echo
echo "============================================================"
echo "Build complete!"
echo "Find your executable at:"
echo "$(pwd)/dist/SeafarerCVAnalyzer"
echo
echo "IMPORTANT:"
echo "Copy your .env file into the dist folder"
echo "(next to the executable)."
echo "============================================================"