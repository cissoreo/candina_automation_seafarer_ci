# =====================================================================
# Preview Dialog - shows extracted data with editable fields
# =====================================================================


from typing import Optional

from template.colors import COLORS
import tkinter as tk


class PreviewDialog(tk.Toplevel):
    def __init__(self, parent, filename: str, data: dict, existing: Optional[dict]):
        super().__init__(parent)
        self.title(f"Preview & Edit — {filename}")
        self.geometry("1100x800")
        self.configure(bg=COLORS["bg"])
        self.data = data
        self.existing = existing
        self.result = None  # ("save", payload) or ("skip", None)

        # Field widgets
        self.pi_widgets = {}  # personal info: simple entries
        self.pi_coded_widgets = {}  # personal info: coded fields
        self.cert_widgets = []  # list of dicts
        self.exp_widgets = []  # list of dicts

        self._build_ui(filename)
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _build_ui(self, filename: str):
        # Header
        header = tk.Frame(self, bg=COLORS["primary_dark"], pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text=f"📄 {filename}",
            bg=COLORS["primary_dark"],
            fg="white",
            font=("Segoe UI", 12, "bold"),
        ).pack()

        # Duplicate warning
        if self.existing:
            warn = tk.Frame(self, bg=COLORS["warning_bg"], pady=10)
            warn.pack(fill="x")
            ex_name = f"{self.existing.get('name','')} {self.existing.get('surname','')}".strip()
            tk.Label(
                warn,
                text=f"⚠ DUPLICATE FOUND  •  Existing: {ex_name}  "
                f"(DOB: {self.existing.get('date_of_birth') or '-'}, "
                f"Email: {self.existing.get('email') or '-'})\n"
                f"Saving will UPDATE the existing record.",
                bg=COLORS["warning_bg"],
                fg="#78350f",
                font=("Segoe UI", 9, "bold"),
                justify="left",
            ).pack(padx=10)

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- TAB 1: Personal Info ---
        pi_tab = self._make_scrollable_tab(notebook, "👤  Personal Information")
        self._build_personal_info_tab(pi_tab)

        # --- TAB 2: Certificates ---
        cert_count = len(self.data.get("certificates", []))
        cert_tab = self._make_scrollable_tab(
            notebook, f"📜  Certificates ({cert_count})"
        )
        self._build_certificates_tab(cert_tab)

        # --- TAB 3: Experiences ---
        exp_count = len(self.data.get("experiences", []))
        exp_tab = self._make_scrollable_tab(notebook, f"⚓  Sea Service ({exp_count})")
        self._build_experiences_tab(exp_tab)

        # --- TAB 4: Raw JSON (for debugging) ---
        raw_tab = ttk.Frame(notebook)
        notebook.add(raw_tab, text="🔍  Raw Data")
        raw_text = scrolledtext.ScrolledText(raw_tab, wrap="word", font=("Consolas", 9))
        raw_text.pack(fill="both", expand=True, padx=5, pady=5)
        raw_text.insert("1.0", json.dumps(self.data, indent=2, ensure_ascii=False))
        raw_text.config(state="disabled")

        # Buttons
        btn_frame = tk.Frame(self, bg=COLORS["bg"], pady=12)
        btn_frame.pack(fill="x", side="bottom")

        tk.Label(
            btn_frame,
            text="🟢 Green = matched code  |  🔴 Red = unmatched (please fix from dropdown)",
            bg=COLORS["bg"],
            fg=COLORS["text_muted"],
            font=("Segoe UI", 8),
        ).pack(side="left", padx=15)

        save_text = (
            "💾 SAVE (Update Existing)" if self.existing else "💾 SAVE (Insert New)"
        )
        tk.Button(
            btn_frame,
            text=save_text,
            bg=COLORS["success"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self._on_save,
        ).pack(side="right", padx=10)

        tk.Button(
            btn_frame,
            text="⏭ SKIP",
            bg=COLORS["text_muted"],
            fg="white",
            font=("Segoe UI", 10),
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self._on_skip,
        ).pack(side="right")

    def _make_scrollable_tab(self, notebook, title):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=title)
        canvas = tk.Canvas(tab, bg=COLORS["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLORS["bg"])
        inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Enable mousewheel scrolling
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        return inner

    # ---------- TAB 1: Personal Info ----------
    def _build_personal_info_tab(self, parent):
        pi = self.data.get("personal_information", {}) or {}

        self._section(parent, "Identity & Contact")
        for key, label in [
            ("name", "First Name *"),
            ("surname", "Surname *"),
            ("middle_name", "Middle Name"),
            ("calling_name", "Calling Name"),
            ("national_full_name", "National Full Name"),
            ("date_of_birth", "Date of Birth (YYYY-MM-DD)"),
            ("place_of_birth", "Place of Birth"),
            ("nationality", "Nationality (3-letter ISO)"),
            ("marital_status", "Marital Status"),
            ("gender", "Gender"),
            ("number_of_children", "Number of Children"),
            ("phone", "Phone"),
            ("mobile", "Mobile"),
            ("email", "Email"),
            ("personal_id", "Personal ID / Passport No"),
            ("accounting_number", "Accounting Number"),
            ("taxation_country", "Taxation Country"),
            ("taxation_id", "Taxation ID"),
        ]:
            self._add_simple_field(parent, key, label, pi.get(key))

        self._section(parent, "Status, Citizenship & Rank (coded fields)")
        self._add_coded_field(
            parent, "status", "Status", pi.get("status_text"), STATUS_LOOKUP
        )
        self._add_coded_field(
            parent, "citizen", "Citizenship", pi.get("citizen_text"), CITIZENSHIP_LOOKUP
        )
        self._add_coded_field(
            parent, "rank", "Current Rank", pi.get("rank_text"), RANK_LOOKUP
        )

        self._section(parent, "Availability & Notes")
        for key, label in [
            ("available_from", "Available From (YYYY-MM-DD)"),
            ("available_to", "Available To (YYYY-MM-DD)"),
            ("fast_note", "Fast Note"),
            ("client_date", "Client Date (YYYY-MM-DD)"),
            ("check_in_note", "Check-in Note"),
        ]:
            self._add_simple_field(parent, key, label, pi.get(key))

        self._section(parent, "Philippines Government IDs (if applicable)")
        for key, label in [
            ("sss", "SSS"),
            ("philhealth", "PhilHealth"),
            ("pag_ibig", "Pag-IBIG"),
        ]:
            self._add_simple_field(parent, key, label, pi.get(key))

        self._section(parent, "Salary & Notice (coded fields)")
        self._add_simple_field(
            parent, "minimum_salary", "Minimum Salary", pi.get("minimum_salary")
        )
        self._add_coded_field(
            parent,
            "salary_currency",
            "Currency",
            pi.get("salary_currency_text"),
            SALARY_CURRENCY_LOOKUP,
        )
        self._add_coded_field(
            parent,
            "salary_type",
            "Salary Type",
            pi.get("salary_type_text"),
            SALARY_TYPE_LOOKUP,
        )
        self._add_simple_field(
            parent, "notice_period", "Notice Period", pi.get("notice_period")
        )
        self._add_coded_field(
            parent,
            "notice_type",
            "Notice Type",
            pi.get("notice_type_text"),
            NOTICE_TYPE_LOOKUP,
        )

        self._section(parent, "Location")
        for key, label in [
            ("current_country", "Current Country (3-letter ISO)"),
            ("current_city", "Current City"),
        ]:
            self._add_simple_field(parent, key, label, pi.get(key))

    # ---------- TAB 2: Certificates ----------
    def _build_certificates_tab(self, parent):
        certs = self.data.get("certificates", []) or []
        if not certs:
            tk.Label(
                parent,
                text="No certificates found in this CV.",
                bg=COLORS["bg"],
                fg=COLORS["text_muted"],
                font=("Segoe UI", 10, "italic"),
            ).pack(pady=20)
            return

        for i, cert in enumerate(certs):
            card = tk.Frame(parent, bg=COLORS["card"], bd=1, relief="solid")
            card.pack(fill="x", padx=10, pady=5)

            tk.Label(
                card,
                text=f"Certificate #{i+1}",
                bg=COLORS["primary_light"],
                fg="white",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                padx=10,
                pady=3,
            ).pack(fill="x")

            cert_widgets = {}

            # Category dropdown
            cat_row = tk.Frame(card, bg=COLORS["card"])
            cat_row.pack(fill="x", padx=10, pady=3)
            tk.Label(
                cat_row,
                text="Category",
                width=22,
                anchor="w",
                bg=COLORS["card"],
                font=("Segoe UI", 9),
            ).pack(side="left")
            cat_var = tk.StringVar(value=cert.get("type_text") or "")
            cat_dd = ttk.Combobox(
                cat_row,
                textvariable=cat_var,
                values=list(CERT_CATEGORIES.keys()),
                width=35,
                state="readonly",
            )
            cat_dd.pack(side="left", padx=5)
            cert_widgets["type"] = cat_var

            # Cert name (free text with code matching)
            name_text = cert.get("name_text") or ""
            # Determine which lookup to use based on category
            category = cert.get("type_text")
            initial_lookup = CERT_CATEGORIES.get(category, CERT_CATEGORIES["Training"])
            name_widget = CodedFieldWidget(
                card, "Certificate Name", name_text, initial_lookup, width=22
            )
            name_widget.pack(fill="x", padx=10, pady=3)

            # When category changes, update the lookup used by the cert name widget
            def make_cat_handler(nw, cv):
                def handler(*args):
                    new_cat = cv.get()
                    if new_cat in CERT_CATEGORIES:
                        nw.lookup = CERT_CATEGORIES[new_cat]
                        nw.code_to_label = CERT_CATEGORIES[new_cat]
                        nw.dropdown_values = [
                            f"{c} — {l}"
                            for c, l in sorted(CERT_CATEGORIES[new_cat].items())
                        ]
                        nw.dropdown.configure(values=nw.dropdown_values)
                        nw._update_match()

                return handler

            cat_var.trace_add("write", make_cat_handler(name_widget, cat_var))

            cert_widgets["name_widget"] = name_widget

            # Simple fields
            simple_fields = [
                ("issue_country", "Issue Country (ISO)"),
                ("issuer", "Issuer"),
                ("issued", "Issued (YYYY-MM-DD)"),
                ("expires", "Expires (YYYY-MM-DD)"),
                ("number", "Certificate Number"),
                ("notes", "Notes"),
            ]
            for key, label in simple_fields:
                row = tk.Frame(card, bg=COLORS["card"])
                row.pack(fill="x", padx=10, pady=2)
                tk.Label(
                    row,
                    text=label,
                    width=22,
                    anchor="w",
                    bg=COLORS["card"],
                    font=("Segoe UI", 9),
                ).pack(side="left")
                entry = tk.Entry(row, font=("Segoe UI", 9))
                entry.pack(side="left", fill="x", expand=True, padx=5)
                if cert.get(key):
                    entry.insert(0, str(cert.get(key)))
                cert_widgets[key] = entry

            # Padding at bottom of card
            tk.Frame(card, bg=COLORS["card"], height=5).pack()

            self.cert_widgets.append(cert_widgets)

    # ---------- TAB 3: Experiences ----------
    def _build_experiences_tab(self, parent):
        exps = self.data.get("experiences", []) or []
        if not exps:
            tk.Label(
                parent,
                text="No sea service entries found in this CV.",
                bg=COLORS["bg"],
                fg=COLORS["text_muted"],
                font=("Segoe UI", 10, "italic"),
            ).pack(pady=20)
            return

        for i, exp in enumerate(exps):
            card = tk.Frame(parent, bg=COLORS["card"], bd=1, relief="solid")
            card.pack(fill="x", padx=10, pady=5)

            vname = exp.get("vessel_name") or "(no name)"
            tk.Label(
                card,
                text=f"Vessel #{i+1}: {vname}",
                bg=COLORS["primary_light"],
                fg="white",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                padx=10,
                pady=3,
            ).pack(fill="x")

            ew = {}

            # Simple text fields
            for key, label in [
                ("vessel_name", "Vessel Name"),
                ("flag", "Flag (3-letter ISO)"),
                ("year_built", "Year Built"),
                ("imo_no", "IMO Number"),
                ("ship_builder", "Ship Builder"),
                ("loa", "LOA (Length, m)"),
                ("dwt", "DWT"),
                ("gt", "Gross Tonnage"),
                ("engine_model", "Engine Model"),
                ("engine_power", "Engine Power"),
                ("location_port", "Location Port"),
                ("location_country", "Location Country (ISO)"),
                ("sign_on", "Sign On (YYYY-MM-DD)"),
                ("sign_off", "Sign Off (YYYY-MM-DD)"),
                ("owner_employer", "Owner / Employer"),
                ("crewing_company", "Crewing Company"),
            ]:
                row = tk.Frame(card, bg=COLORS["card"])
                row.pack(fill="x", padx=10, pady=2)
                tk.Label(
                    row,
                    text=label,
                    width=22,
                    anchor="w",
                    bg=COLORS["card"],
                    font=("Segoe UI", 9),
                ).pack(side="left")
                entry = tk.Entry(row, font=("Segoe UI", 9))
                entry.pack(side="left", fill="x", expand=True, padx=5)
                if exp.get(key) is not None:
                    entry.insert(0, str(exp.get(key)))
                ew[key] = entry

            # Coded fields
            ew["type_widget"] = self._inline_coded(
                card, "Vessel Type", exp.get("type_text"), VESSEL_TYPE_LOOKUP
            )
            ew["pumping_system_widget"] = self._inline_coded(
                card,
                "Pumping System",
                exp.get("pumping_system_text"),
                VESSEL_PUMP_LOOKUP,
            )
            ew["cargo_handling_gear_widget"] = self._inline_coded(
                card,
                "Cargo Handling Gear",
                exp.get("cargo_handling_gear_text"),
                VESSEL_GEAR_LOOKUP,
            )
            ew["engine_type_widget"] = self._inline_coded(
                card, "Engine Type", exp.get("engine_type_text"), ENGINE_TYPE_LOOKUP
            )
            ew["dp_type_widget"] = self._inline_coded(
                card, "DP Type", exp.get("dp_type_text"), DP_TYPE_LOOKUP
            )
            ew["dp_manufacturer_widget"] = self._inline_coded(
                card,
                "DP Manufacturer",
                exp.get("dp_manufacturer_text"),
                DP_MANUFACTURER_LOOKUP,
            )
            ew["rank_widget"] = self._inline_coded(
                card, "Rank on this Vessel", exp.get("rank_text"), EXP_RANK_LOOKUP
            )
            ew["off_reason_widget"] = self._inline_coded(
                card, "Off Reason", exp.get("off_reason_text"), OFF_REASON_LOOKUP
            )

            # Operation type (numeric, not coded)
            row = tk.Frame(card, bg=COLORS["card"])
            row.pack(fill="x", padx=10, pady=2)
            tk.Label(
                row,
                text="Operation Type (number)",
                width=22,
                anchor="w",
                bg=COLORS["card"],
                font=("Segoe UI", 9),
            ).pack(side="left")
            entry = tk.Entry(row, font=("Segoe UI", 9))
            entry.pack(side="left", fill="x", expand=True, padx=5)
            if exp.get("operation_type") is not None:
                entry.insert(0, str(exp.get("operation_type")))
            ew["operation_type"] = entry

            tk.Frame(card, bg=COLORS["card"], height=5).pack()
            self.exp_widgets.append(ew)

    def _inline_coded(self, parent, label, text_value, lookup):
        w = CodedFieldWidget(parent, label, text_value, lookup)
        w.pack(fill="x", padx=10, pady=2)
        return w

    # ---------- Helpers ----------
    def _section(self, parent, title):
        tk.Label(
            parent,
            text=title,
            bg=COLORS["primary"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=10,
            pady=5,
        ).pack(fill="x", padx=10, pady=(15, 5))

    def _add_simple_field(self, parent, key, label, value):
        row = tk.Frame(parent, bg=COLORS["bg"])
        row.pack(fill="x", padx=10, pady=2)
        tk.Label(
            row, text=label, width=30, anchor="w", bg=COLORS["bg"], font=("Segoe UI", 9)
        ).pack(side="left")
        entry = tk.Entry(row, font=("Segoe UI", 9))
        entry.pack(side="left", fill="x", expand=True, padx=5)
        if value is not None:
            entry.insert(0, str(value))
        self.pi_widgets[key] = entry

    def _add_coded_field(self, parent, key, label, text_value, lookup):
        row = tk.Frame(parent, bg=COLORS["bg"])
        row.pack(fill="x", padx=10, pady=2)
        w = CodedFieldWidget(row, label, text_value, lookup, width=30)
        w.pack(fill="x")
        self.pi_coded_widgets[key] = w

    # ---------- Buttons ----------
    def _on_save(self):
        # Collect personal info
        pi = {}
        for key, widget in self.pi_widgets.items():
            v = widget.get().strip()
            if v == "":
                pi[key] = None
                continue
            # numeric fields
            if key in ("number_of_children", "notice_period"):
                try:
                    pi[key] = int(v)
                except ValueError:
                    pi[key] = None
            elif key in ("minimum_salary",):
                try:
                    pi[key] = float(v)
                except ValueError:
                    pi[key] = None
            else:
                pi[key] = v

        for key, w in self.pi_coded_widgets.items():
            pi[key] = w.get_code()

        # Validation
        if not pi.get("name") or not pi.get("surname"):
            messagebox.showerror("Missing data", "First Name and Surname are required.")
            return

        # Collect certificates
        certs = []
        for cw in self.cert_widgets:
            cert = {}
            cert["type"] = cw["type"].get() or None
            cert["cert_id"] = cw["name_widget"].get_code()
            cert["cert_name"] = cw["name_widget"].get_text()
            for k in (
                "issue_country",
                "issuer",
                "issued",
                "expires",
                "number",
                "notes",
            ):
                v = cw[k].get().strip() if k in cw else ""
                cert[k] = v if v else None
            certs.append(cert)

        # Collect experiences
        exps = []
        for ew in self.exp_widgets:
            exp = {}
            for k in (
                "vessel_name",
                "flag",
                "imo_no",
                "ship_builder",
                "engine_model",
                "location_port",
                "location_country",
                "sign_on",
                "sign_off",
                "owner_employer",
                "crewing_company",
            ):
                v = ew[k].get().strip() if k in ew else ""
                exp[k] = v if v else None
            # numeric
            for k in ("year_built", "operation_type"):
                v = ew[k].get().strip() if k in ew else ""
                try:
                    exp[k] = int(v) if v else None
                except ValueError:
                    exp[k] = None
            for k in ("loa", "dwt", "gt", "engine_power"):
                v = ew[k].get().strip() if k in ew else ""
                try:
                    exp[k] = float(v) if v else None
                except ValueError:
                    exp[k] = None
            # coded
            for k in (
                "type",
                "pumping_system",
                "cargo_handling_gear",
                "engine_type",
                "dp_type",
                "dp_manufacturer",
                "rank",
                "off_reason",
            ):
                exp[k] = ew[f"{k}_widget"].get_code()
            exps.append(exp)

        self.result = (
            "save",
            {"personal_information": pi, "certificates": certs, "experiences": exps},
        )
        self.destroy()

    def _on_skip(self):
        self.result = ("skip", None)
        self.destroy()

