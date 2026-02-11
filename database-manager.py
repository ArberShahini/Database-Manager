import json
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from sqlalchemy import create_engine, text
import env


def safe_table_name_from_filename(path: str) -> str:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    if not name:
        raise ValueError("Invalid filename.")

    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        raise ValueError(
            "Invalid JSON filename for table mapping. "
            "Use only letters, numbers, underscore (e.g. klient.json, detaje_transaksioni.json)."
        )
    return f"dbo.[{name}]"


def load_rows_from_json(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and isinstance(data.get("rows"), list):
        rows = data["rows"]
    else:
        raise ValueError("JSON must be a list of objects OR an object with key 'rows' containing a list.")

    if not rows:
        raise ValueError("JSON contains 0 rows.")
    if not all(isinstance(r, dict) for r in rows):
        raise ValueError("Each row must be a JSON object (dictionary).")

    return rows


def normalize_rows(rows: list[dict]) -> tuple[list[str], list[dict]]:
    all_cols = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                all_cols.append(k)

    if not all_cols:
        raise ValueError("JSON rows have no fields/keys.")

    for c in all_cols:
        if not re.fullmatch(r"[A-Za-z0-9_]+", c):
            raise ValueError(
                f"Invalid column name in JSON: '{c}'. "
                "Use only letters, numbers, underscore."
            )

    normalized = [{c: r.get(c, None) for c in all_cols} for r in rows]
    return all_cols, normalized


class GenericJsonImporter(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Palette (light green dominant) ---
        self.COL_BG = "#E9F7EF"       # very light green background
        self.COL_CARD = "#F4FBF7"     # card background
        self.COL_ACCENT = "#2E7D32"   # green accent
        self.COL_ACCENT2 = "#43A047"  # hover/secondary green
        self.COL_TEXT = "#163A1D"     # dark green text
        self.COL_MUTED = "#3B5A40"    # muted text
        self.COL_BORDER = "#CDE9D6"   # subtle border
        self.COL_ERR = "#B71C1C"

        self.title("JSON Importer → SQL Server")
        self.configure(bg=self.COL_BG)
        self.geometry("820x320")
        self.minsize(820, 320)
        self.resizable(False, False)

        self.json_path_var = tk.StringVar()

        # Engine
        self.engine = create_engine(env.DB_URL, future=True)

        # ttk styling
        self._setup_styles()

        # Layout
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()

        # Use a native theme but override colors (works best with 'clam')
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "App.TFrame",
            background=self.COL_BG
        )
        style.configure(
            "Card.TFrame",
            background=self.COL_CARD,
            relief="flat"
        )
        style.configure(
            "Title.TLabel",
            background=self.COL_BG,
            foreground=self.COL_TEXT,
            font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.COL_BG,
            foreground=self.COL_MUTED,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Field.TLabel",
            background=self.COL_CARD,
            foreground=self.COL_TEXT,
            font=("Segoe UI", 10, "bold")
        )
        style.configure(
            "Hint.TLabel",
            background=self.COL_CARD,
            foreground=self.COL_MUTED,
            font=("Segoe UI", 9)
        )
        style.configure(
            "Status.TLabel",
            background=self.COL_BG,
            foreground=self.COL_MUTED,
            font=("Segoe UI", 9)
        )

        # Buttons
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
            foreground="white",
            background=self.COL_ACCENT,
            borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.COL_ACCENT2)]
        )

        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=(12, 8),
            foreground=self.COL_TEXT,
            background="#DFF3E7",
            borderwidth=0
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#CFECDD")]
        )

        # Entry
        style.configure(
            "Green.TEntry",
            fieldbackground="white",
            foreground=self.COL_TEXT,
            bordercolor=self.COL_BORDER,
            lightcolor=self.COL_BORDER,
            darkcolor=self.COL_BORDER,
            padding=8
        )

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True, padx=18, pady=16)

        # Header
        header = ttk.Frame(root, style="App.TFrame")
        header.pack(fill="x")

        ttk.Label(header, text="JSON Importer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Ngarko një JSON me te dhenat qe duhet te ruhen ne bazen e te dhenave",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        # Card
        card = ttk.Frame(root, style="Card.TFrame")
        card.pack(fill="both", expand=True, pady=(14, 10))

        # give card padding via inner frame
        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        # Field label
        ttk.Label(inner, text="JSON file", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            inner,
            text="Tabela target do të jetë: dbo.[emri_i_file.json pa .json]",
            style="Hint.TLabel"
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 10))

        # Entry + Buttons row
        self.path_entry = ttk.Entry(inner, textvariable=self.json_path_var, width=74, style="Green.TEntry")
        self.path_entry.grid(row=2, column=0, sticky="we", pady=(0, 12))

        browse_btn = ttk.Button(inner, text="Browse…", style="Secondary.TButton", command=self.browse_json)
        browse_btn.grid(row=2, column=1, padx=(10, 0), pady=(0, 12))

        submit_btn = ttk.Button(inner, text="Submit Import", style="Primary.TButton", command=self.submit)
        submit_btn.grid(row=3, column=0, sticky="w")

        # Make the entry expand
        inner.columnconfigure(0, weight=1)

        # Status bar
        self.status = ttk.Label(root, text="Gati. Zgjidh një JSON për të importuar.", style="Status.TLabel")
        self.status.pack(fill="x", pady=(6, 0))

        # Optional: simple hover effect for entry (focus highlight)
        self.path_entry.bind("<FocusIn>", lambda _e: self._set_status("Shkruaj ose zgjidh path-in e file-it JSON."))
        self.path_entry.bind("<FocusOut>", lambda _e: self._set_status("Gati."))

    def _set_status(self, msg: str, error: bool = False):
        self.status.configure(foreground=(self.COL_ERR if error else self.COL_MUTED))
        self.status.configure(text=msg)

    def browse_json(self):
        path = filedialog.askopenfilename(
            title="Select a JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.json_path_var.set(path)
            try:
                target_table = safe_table_name_from_filename(path)
                self._set_status(f"Target: {target_table}")
            except Exception:
                self._set_status("Filename nuk mund të përdoret për tabelë (lejohet vetëm A-Z, 0-9, _).", error=True)

    def submit(self):
        try:
            path = self.json_path_var.get().strip()
            if not path:
                raise ValueError("Zgjidh një file JSON.")
            if not os.path.isfile(path):
                raise ValueError("File nuk ekziston.")
            if not path.lower().endswith(".json"):
                raise ValueError("Duhet një file .json.")

            target_table = safe_table_name_from_filename(path)
            rows = load_rows_from_json(path)
            cols, normalized = normalize_rows(rows)

            col_list_sql = ", ".join(f"[{c}]" for c in cols)
            param_list_sql = ", ".join(f":{c}" for c in cols)
            stmt = text(f"INSERT INTO {target_table} ({col_list_sql}) VALUES ({param_list_sql})")

            self._set_status("Duke importuar…")
            with self.engine.begin() as conn:
                conn.execute(stmt, normalized)

            self._set_status(f"✅ U futën {len(normalized)} rekord(e) në {target_table}.")
            messagebox.showinfo("Success", f"Inserted {len(normalized)} rows into {target_table}")

        except Exception as e:
            self._set_status(f"❌ Gabim: {e}", error=True)
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = GenericJsonImporter()
    app.mainloop()
