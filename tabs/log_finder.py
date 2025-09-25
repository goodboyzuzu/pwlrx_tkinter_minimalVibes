import customtkinter as ctk
from tkinter import ttk, font as tkfont
import tkinter as tk
import os
from datetime import datetime, timezone
from .utils import get_matching_directories, process_log_files

LOGS_DIRECTORY = r"C:\Users\gohzu\Desktop\pwlrx_tkinter_minimalVibe\n69r"

class LogFinder(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        row = ctk.CTkFrame(self, height=120)
        row.pack(fill="x")
        row.pack_propagate(False)

        label = ctk.CTkLabel(row, text="Search lot id: ", anchor="w")
        label.pack(side="left")

        self.textbox = ctk.CTkTextbox(row)
        self.textbox.pack(side="left", fill="x", expand=True)
        self.textbox.bind("<Shift-Return>", self._search_logs)

        button = ctk.CTkButton(row, text="Search", width=80, command=self._search_logs)
        button.pack(side="right")

        table_row = ctk.CTkFrame(self)
        table_row.pack(fill="both", expand=True, pady=12, padx=12)

        heading_font = tkfont.Font(weight="bold", size=9)
        ttk.Style().configure("Treeview.Heading", font=heading_font)

        self.tree = ttk.Treeview(table_row, columns=("offset", "log_folder", "date", "cycle_count"), show="headings")
        self.tree.heading("offset", text="Offset", anchor="center")
        self.tree.heading("log_folder", text="Log Folder", anchor="center")
        self.tree.heading("date", text="Date", anchor="center")
        self.tree.heading("cycle_count", text="Cycle Count", anchor="center")
        self.tree.column("offset", anchor="center")
        self.tree.column("log_folder", width=400, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("cycle_count", anchor="center")
        self.tree.pack(fill="both", expand=True)

        crunch_button = ctk.CTkButton(self, text="Crunch Data", command=self._crunch_data)
        crunch_button.pack(pady=10)

        self._edit_entry = None
        self.tree.bind("<Double-1>", self._on_double_click)

        # Bind right-click to show context menu (Button-3 for Windows/Linux, Button-2 for some mac clients)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Button-2>", self._show_context_menu)

        # Create a context menu using tkinter.Menu (customtkinter has no CTkMenu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Remove Row", command=self._remove_row)

        self._selected_row_id = None

    def _search_logs(self, event=None):
        self.tree.delete(*self.tree.get_children())
        lines = [line.strip() for line in self.textbox.get("1.0", "end").splitlines() if line.strip()]

        try:
            dirs = get_matching_directories(LOGS_DIRECTORY, lines)
        except Exception:
            dirs = []

        for d in dirs:
            folder_path = os.path.join(LOGS_DIRECTORY, d)
            try:
                files = (os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))
            except Exception:
                files = []

            try:
                timestamp = int(d.split(".")[-1])
                date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%m-%d %H:%M')
            except ValueError:
                date_str = "Invalid Date"

            cycle_val = process_log_files(files)
            cycle = cycle_val.split("_")[0] if "_" in cycle_val else cycle_val
            self.tree.insert("", "end", values=("-", d, date_str, cycle))

        self._sort_table(["date", "log_folder"], reverse=False)
        if event is not None:
            return "break"

    def _sort_table(self, columns, reverse):
        if not isinstance(columns, list):
            columns = [columns]

        rows = [(tuple(self.tree.set(k, col) for col in columns), k) for k in self.tree.get_children("")]
        rows.sort(reverse=reverse, key=lambda x: x[0])

        for index, (val, k) in enumerate(rows):
            self.tree.move(k, "", index)

    def _on_double_click(self, event):
        if self._edit_entry:
            self._edit_entry.destroy()
            self._edit_entry = None

        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if not row_id or not col or col == "#0":
            return

        bbox = self.tree.bbox(row_id, col)
        if not bbox:
            return
        x, y, width, height = bbox

        tree_width = self.tree.winfo_width()
        margin = 10
        if col == f"#{len(self.tree['columns'])}":
            if x + width > tree_width - margin:
                x = max(0, tree_width - width - margin)

        try:
            col_index = int(col.replace("#", "")) - 1
            col_name = self.tree["columns"][col_index]
        except Exception:
            return

        current_value = self.tree.set(row_id, column=col_name)
        self._edit_entry = ctk.CTkEntry(self.tree, width=width, height=height)
        self._edit_entry.insert(0, current_value)
        try:
            self._edit_entry.select_range(0, "end")
        except Exception:
            pass

        self._edit_entry.place(x=x, y=y)
        self._edit_entry.focus()
        self._edit_entry.bind("<Return>", lambda e, rid=row_id, cname=col_name: self._save_edit(rid, cname))
        self._edit_entry.bind("<FocusOut>", lambda e, rid=row_id, cname=col_name: self._save_edit(rid, cname))

    def _save_edit(self, row_id, col_name):
        if self._edit_entry:
            new_value = self._edit_entry.get().strip()
            if new_value:
                self.tree.set(row_id, column=col_name, value=new_value)
            self._edit_entry.destroy()
            self._edit_entry = None

    def _crunch_data(self):
        print("Crunching data...")

    def _show_context_menu(self, event):
        # Identify the row under the cursor
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self._selected_row_id = row_id  # Store the selected row ID
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _remove_row(self):
        if self._selected_row_id:
            self.tree.delete(self._selected_row_id)  # Remove the selected row
            self._selected_row_id = None