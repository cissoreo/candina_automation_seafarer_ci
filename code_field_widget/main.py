# =====================================================================
# Reusable Field-with-Code widget
#   Shows: label | text entry | "→ code: 569 ✓"  OR  "⚠ UNMATCHED" + dropdown
# =====================================================================


class CodedFieldWidget(tk.Frame):
    """A field that maps text to a code using a lookup dict."""

    def __init__(self, parent, label, text_value, lookup_dict, width=22):
        super().__init__(parent, bg=COLORS["card"])
        self.lookup = lookup_dict
        # Reverse lookup for dropdown values
        self.code_to_label = lookup_dict
        self.dropdown_values = [
            f"{code} — {label}" for code, label in sorted(lookup_dict.items())
        ]

        # Label
        tk.Label(
            self,
            text=label,
            width=width,
            anchor="w",
            bg=COLORS["card"],
            font=("Segoe UI", 9),
        ).pack(side="left")

        # Text entry
        self.text_var = tk.StringVar(value=text_value or "")
        self.entry = tk.Entry(
            self, textvariable=self.text_var, font=("Segoe UI", 9), width=22
        )
        self.entry.pack(side="left", padx=(0, 5))
        self.text_var.trace_add("write", self._on_text_change)

        # Status label
        self.status_label = tk.Label(
            self,
            text="",
            bg=COLORS["card"],
            font=("Segoe UI", 9, "bold"),
            width=18,
            anchor="w",
        )
        self.status_label.pack(side="left", padx=(0, 5))

        # Dropdown (initially hidden)
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self,
            textvariable=self.dropdown_var,
            values=self.dropdown_values,
            width=30,
            state="readonly",
        )
        self.dropdown.pack(side="left", padx=(0, 5))
        self.dropdown.bind("<<ComboboxSelected>>", self._on_dropdown_select)

        self.code = None
        self._update_match()

    def _on_text_change(self, *args):
        self._update_match()

    def _on_dropdown_select(self, event):
        sel = self.dropdown_var.get()
        if not sel:
            return
        code_str = sel.split(" — ")[0]
        self.code = int(code_str)
        label = self.code_to_label.get(self.code, "")
        self.text_var.set(label)
        self.status_label.config(text=f"✓ code: {self.code}", fg=COLORS["success"])

    def _update_match(self):
        text = self.text_var.get().strip()
        if not text:
            self.code = None
            self.status_label.config(text="(empty)", fg=COLORS["text_muted"])
            self.dropdown.set("")
            return
        code, label, conf = map_text_to_code(text, self.lookup)
        if code is not None and conf >= 0.7:
            self.code = code
            self.status_label.config(text=f"✓ code: {code}", fg=COLORS["success"])
            self.dropdown.set("")
        else:
            self.code = None
            self.status_label.config(text="⚠ UNMATCHED", fg=COLORS["danger"])
            self.dropdown.set("")

    def get_code(self):
        return self.code

    def get_text(self):
        return self.text_var.get().strip() or None
