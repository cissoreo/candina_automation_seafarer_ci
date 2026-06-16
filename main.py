"""
main.py
--------
Seafarer CV Analyzer — Main GUI

Workflow:
    1. User selects one or more CV files
    2. For each file:
        - Extract text locally
        - Send to Claude → readable JSON
        - Map text values to codes locally (fuzzy match)
        - Check Supabase for duplicate
        - Show preview dialog with:
         * Editable text values
         * Mapped code preview
         * Dropdowns for unmatched fields
        - On confirm: insert new OR update existing
    3. Show summary
"""

import sys
from pathlib import Path
from app.main import App

# Path setup
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    SRC_DIR = (
        Path(sys._MEIPASS) / "src" if hasattr(sys, "_MEIPASS") else BASE_DIR / "src"
    )   
else:
    BASE_DIR = Path(__file__).parent
    SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
