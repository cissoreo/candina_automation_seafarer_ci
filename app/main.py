from ast import excepthandler
from pathlib import Path
import threading
from tkinter import filedialog, scrolledtext, ttk
import traceback
from typing import Optional

from app.log_msg import log_msg
from automation.main import PlayWright
from src.claude_analyzer import ClaudeAnalyzer
from config import load_config
from src.cv_extractor import extract_text, get_supported_extensions
from preview_dialog.main import PreviewDialog
from src.supabase_manager import SupabaseManager
from template.colors import COLORS
import tkinter as tk
from playwright.sync_api import sync_playwright

from template.errors import IsExists


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚓ Seafarer CV Analyzer")
        self.geometry("950x680")
        self.configure(bg=COLORS["bg"])

        self.config_data = load_config()
        self.analyzer: Optional[ClaudeAnalyzer] = None
        # self.db: Optional[SupabaseManager] = None
        self.files: list = []

        self.stats = {
            "processed": 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "cost": 0.0,
        }

        self._build_ui()
        self._init_services()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["primary_dark"], pady=15)
        header.pack(fill="x")
        tk.Label(
            header,
            text="⚓ Seafarer CV Analyzer",
            bg=COLORS["primary_dark"],
            fg="white",
            font=("Segoe UI", 18, "bold"),
        ).pack()
        tk.Label(
            header,
            text="Extract → Preview → Save to Supabase",
            bg=COLORS["primary_dark"],
            fg="#cbd5e1",
            font=("Segoe UI", 9),
        ).pack(pady=(3, 0))

        # Control row
        ctrl = tk.Frame(self, bg=COLORS["bg"], pady=15)
        ctrl.pack(fill="x", padx=20)

        self.select_btn = tk.Button(
            ctrl,
            text="📂  Select CV Files",
            bg=COLORS["primary_light"],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.select_files,
        )
        self.select_btn.pack(side="left", padx=(0, 10))

        self.process_btn = tk.Button(
            ctrl,
            text="▶  Process Files",
            bg=COLORS["success"],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.start_processing,
            state="disabled",
        )
        self.process_btn.pack(side="left")

        self.file_count_label = tk.Label(
            ctrl,
            text="No files selected",
            bg=COLORS["bg"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 10),
        )
        self.file_count_label.pack(side="left", padx=20)

        # Stats card
        stats_card = tk.Frame(self, bg="#e0e7ff")
        stats_card.pack(fill="x", padx=20, pady=(0, 10))
        self.stats_label = tk.Label(
            stats_card,
            text=self._stats_text(),
            bg="#e0e7ff",
            fg=COLORS["primary_dark"],
            font=("Segoe UI", 9, "bold"),
            pady=8,
        )
        self.stats_label.pack()

        # Progress bar
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=(0, 10))

        # Log
        log_card = tk.Frame(self, bg=COLORS["bg"])
        log_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        tk.Label(
            log_card,
            text="📋  Activity Log",
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")
        self.log = scrolledtext.ScrolledText(
            log_card,
            wrap="word",
            font=("Consolas", 9),
            bg=COLORS["log_bg"],
            fg=COLORS["log_text"],
        )
        self.log.pack(fill="both", expand=True, pady=(5, 0))
        self.log.tag_config("info", foreground="#93c5fd")
        self.log.tag_config("success", foreground="#86efac")
        self.log.tag_config("warn", foreground="#fde047")
        self.log.tag_config("error", foreground="#fca5a5")

    def _stats_text(self):
        s = self.stats
        return (
            f"📊  Processed: {s['processed']}  •  ➕ Inserted: {s['inserted']}  •  "
            f"♻ Updated: {s['updated']}  •  ⏭ Skipped: {s['skipped']}  •  "
            f"❌ Errors: {s['errors']}  •  💵 Est. cost: ${s['cost']:.4f}"
        )

    def _init_services(self):
        if not self.config_data:
            BASE_DIR = Path(__file__).resolve().parent.parent
            log_msg(self, 
                f"⚠ .env file not found at {BASE_DIR / '.env'}\nCreate one (see .env.example) and restart.",
                "error",
            )
            self.select_btn.config(state="disabled")
            return

        missing = []
        if not self.config_data["anthropic_api_key"] or self.config_data[
            "anthropic_api_key"
        ].startswith("sk-ant-api03-xxx"):
            missing.append("ANTHROPIC_API_KEY")
        if not self.config_data["supabase_url"]:
            missing.append("SUPABASE_URL")
        if not self.config_data["supabase_key"]:
            missing.append("SUPABASE_KEY")

        if missing:
            log_msg(self, f"⚠ Missing values in .env: {', '.join(missing)}", "error")
            self.select_btn.config(state="disabled")
            return

        try:
            self.analyzer = ClaudeAnalyzer(
                self.config_data["anthropic_api_key"],
                self.config_data["anthropic_model"],
            )
            self.db = SupabaseManager(
                self.config_data["supabase_url"], self.config_data["supabase_key"]
            )
            log_msg(self, 
                f"✓ Connected. Using model: {self.config_data['anthropic_model']}",
                "success",
            )
        except Exception as e:
            log_msg(self, f"⚠ Failed to initialize services: {e}", "error")
            self.select_btn.config(state="disabled")

    def update_stats(self):
        self.stats_label.config(text=self._stats_text())

    def select_files(self):
        exts = get_supported_extensions()
        filetypes = [
            ("All supported", " ".join(f"*{e}" for e in exts)),
            ("PDF", "*.pdf"),
            ("Word", "*.docx *.doc"),
            ("Excel", "*.xlsx *.xls"),
        ]
        files = filedialog.askopenfilenames(
            title="Select Seafarer CVs", filetypes=filetypes
        )
        if files:
            self.files = list(files)
            self.file_count_label.config(text=f"📁  {len(self.files)} file(s) selected")
            self.process_btn.config(state="normal")
            log_msg(self, f"Selected {len(self.files)} file(s).", "info")

    def start_processing(self):
        self.process_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0
        threading.Thread(target=self.process_all_files, daemon=True).start()

    def process_all_files(self):
        while self.files:
            filepath = self.files.pop(0)  # ambil dan hapus file pertama
            try:
                self.process_one_file(filepath)
                log_msg(self, f"Delete {Path(filepath).name} from queue", "info")

            except IsExists as e:
                self.stats["errors"] += 1

                log_msg(
                    self,
                    f"  ✗ ERROR: {e}",
                    "error"
                )

                log_msg(
                    self,
                    traceback.format_exc(),
                    "error"
                )

            except Exception as e:
                self.stats["errors"] += 1

                log_msg(
                    self,
                    f"  ✗ ERROR: {e}",
                    "error"
                )

                log_msg(
                    self,
                    traceback.format_exc(),
                    "error"
                )

            self.stats["processed"] += 1
            self.progress["value"] = self.stats["processed"]
            self.file_count_label.config(
                text=f"📁 {len(self.files)} file(s) remaining"
            )

            self.update_stats()

        log_msg(self, "\n═══ DONE ═══", "success")

        log_msg(
            self,
            f"➕ Inserted: {self.stats['inserted']}  "
            f"♻ Updated: {self.stats['updated']}  "
            f"⏭ Skipped: {self.stats['skipped']}  "
            f"❌ Errors: {self.stats['errors']}",
            "success",
        )

        log_msg(
            self,
            f"💵 Total cost: ${self.stats['cost']:.4f}",
            "success"
        )

        self.select_btn.config(state="normal")
        self.process_btn.config(state="normal")
        
    def process_one_file(self, filepath: str):
        filename = Path(filepath).name
        log_msg(self, f"\n→ Processing: {filename}", "info")

        # Step 1: extract text locally
        log_msg(self, "  • Extracting text...", "info")
        text = extract_text(filepath)
        if not text or text.startswith("[ERROR"):
            raise RuntimeError(f"Could not extract text: {text}")
        log_msg(self, f"    extracted {len(text)} chars", "info")

        # Step 2: send to Claude
        log_msg(self, "  • Analyzing with Claude...", "info")
        data = self.analyzer.analyze_cv(text)
        usage = self.analyzer.last_usage
        cost = self.analyzer.estimate_cost()
        self.stats["cost"] += cost
        log_msg(self, 
            f"    tokens: {usage['input_tokens']} in / {usage['output_tokens']} out  (~${cost:.4f})",
            "info",
        )

        pi = data.get("personal_information", {}) or {}
        log_msg(self, "  • Opening in Crew Inspector...", "info")
        
        # PLAYWRIGHT
        with sync_playwright() as p:
            browser, name, status_progress, seafarer_id = PlayWright.playwright_main(data, p)
            
            if name and status_progress == "added":
                self.stats["inserted"] += 1
                log_msg(self, f"  ✓ Processed Done: {name} | Seafarer ID: {seafarer_id}", "success")
                
            if name and status_progress == "is_exist":
                self.stats["skipped"] += 1
                log_msg(self, f"  ⏭ Skipped: {name}", "warn")
                
            if name and status_progress == "added_with_errors":
                self.stats["inserted"] += 1
                log_msg(self, f"  ✓ Processed done but with errors: {name} | Seafarer ID: {seafarer_id}", "warn") 
            
            browser.close()
        return
    
        existing = self.db.find_existing(
            name=pi.get("name"),
            surname=pi.get("surname"),
            date_of_birth=pi.get("date_of_birth"),
            email=pi.get("email"),
        )
        if existing:
            ex_name = f"{existing.get('name','')} {existing.get('surname','')}".strip()
            log_msg(self, 
                f"  ⚠ Duplicate: {ex_name} (id={existing['id'][:8]}...)", "warn"
            )
        else:
            log_msg(self, 
                f"  ✓ New: {pi.get('name','?')} {pi.get('surname','?')}", "success"
            )

        # Step 4: preview dialog
        action, payload = self._show_preview_blocking(filename, data, existing)
        if action == "skip":
            self.stats["skipped"] += 1
            log_msg(self, "  ⏭ Skipped by user", "warn")
            return

        # Step 5: save to db
        if existing:
            log_msg(self, "  • Updating existing record...", "info")
            self.db.update_seafarer(
                existing["id"],
                payload["personal_information"],
                payload["certificates"],
                payload["experiences"],
                source_filename=filename,
            )
            self.stats["updated"] += 1
            log_msg(self, "  ✓ Updated successfully", "success")
        else:
            log_msg(self, "  • Inserting new record...", "info")
            new_id = self.db.insert_seafarer(
                payload["personal_information"],
                payload["certificates"],
                payload["experiences"],
                source_filename=filename,
            )
            self.stats["inserted"] += 1
            log_msg(self, f"  ✓ Inserted (id={new_id[:8]}...)", "success")

    def _show_preview_blocking(self, filename, data, existing):
        result_holder = {}
        done = threading.Event()

        def show():
            dlg = PreviewDialog(self, filename, data, existing)
            result_holder["result"] = dlg.result
            done.set()

        self.after(0, show)
        done.wait()
        return result_holder.get("result") or ("skip", None)
