import customtkinter as ctk
from tkinter import ttk, font as tkfont
import os
from datetime import datetime, timezone  # Updated import to include timezone
from .utils import get_matching_directories, process_log_files

LOGS_DIRECTORY = r"\\fsnvemaffs\nve_maf\axcel\pwlrx_n69r"
# LOGS_DIRECTORY = r"C:\Users\gohzu\Desktop\pwlrx_tkinter_minimalVibe\n69r"

class LogFinder(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # row
        row = ctk.CTkFrame(self, height=120)
        row.pack(fill="x")
        row.pack_propagate(False)  # prevent auto-resizing

        label = ctk.CTkLabel(row, text="Search lot id: ",anchor="w")
        label.pack(side="left")

        self.textbox = ctk.CTkTextbox(row)
        self.textbox.pack(side="left", fill="x", expand=True)

        # bind Shift+Enter to trigger search (handler accepts optional event)
        self.textbox.bind("<Shift-Return>", self._search_logs)

        button = ctk.CTkButton(row, text="Search", width=80, command=self._search_logs)
        button.pack(side="right")

        table_row = ctk.CTkFrame(self)
        table_row.pack(fill="both", expand=True, pady=12, padx=12)

        # Configure heading font (unchanged)
        heading_font = tkfont.Font(weight="bold", size=9)
        ttk.Style().configure("Treeview.Heading", font=heading_font)


        self.tree = ttk.Treeview(table_row, columns=("log_folder", "date", "cycle_count", "offset"), show="headings")
        self.tree.heading("log_folder", text="Log Folder", anchor="center")
        self.tree.heading("date", text="Date", anchor="center")  # Added new column heading
        self.tree.heading("cycle_count", text="Cycle Count", anchor="center")
        self.tree.heading("offset", text="Offset", anchor="center")
        self.tree.column("log_folder", width=400, anchor="center")  # Center align values
        self.tree.column("date", width=150, anchor="center")  # Added new column width
        self.tree.column("cycle_count", anchor="center")  # Center align values
        self.tree.column("offset", anchor="center")  # Center align values
        self.tree.pack(fill="both", expand=True)

        self._edit_entry = None
        self.tree.bind("<Double-1>", self._on_double_click)

    # accept optional event so this can be used as a key binding callback
    def _search_logs(self, event=None):
        # Clear previous results
        self.tree.delete(*self.tree.get_children())

        # Get input lines
        lines = [line.strip() for line in self.textbox.get("1.0", "end").splitlines() if line.strip()]

        # Get matching directories
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

            # Extract Unix timestamp from directory name and convert to date
            try:
                timestamp = int(d.split(".")[-1])  # Extract the last part of the directory name
                date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                date_str = "Invalid Date"

            # Process log files and get cycle value
            cycle_val = process_log_files(files)
            cycle = cycle_val.split("_")[0] if "_" in cycle_val else cycle_val  # Extract only the {cycle} part

            # Determine tag based on the first 10 characters of log_folder
            tag = d[:10]
            self.tree.insert("", "end", values=(d, date_str, cycle, "-"))

        # Sort the table by log_folder column after inserting rows
        self._sort_table("log_folder", reverse=False)

        # Prevent Text widget from inserting a newline when called from a key binding
        if event is not None:
            return "break"

    def _sort_table(self, column, reverse):
        # Get all rows from the tree
        rows = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]

        # Sort rows based on the column value
        rows.sort(reverse=reverse, key=lambda x: x[0])

        # Rearrange rows in the tree
        for index, (val, k) in enumerate(rows):
            self.tree.move(k, "", index)

    def _on_double_click(self, event):
        # Destroy existing editor if any
        if self._edit_entry:
            self._edit_entry.destroy()
            self._edit_entry = None

        # Identify the row and column under the click
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        # Ignore clicks outside rows or on the tree's icon column
        if not row_id or not col or col == "#0":
            return

        # Get bbox for the cell; bbox may be empty if column not visible
        bbox = self.tree.bbox(row_id, col)
        if not bbox:
            return
        x, y, width, height = bbox

        # Shift bbox to the left by 5 pixels
        x -= 5

        # Map column token like "#1" to actual column name used in tree["columns"]
        try:
            col_index = int(col.replace("#", "")) - 1
            col_name = self.tree["columns"][col_index]
        except Exception:
            return

        # Create CTkEntry with width/height passed to constructor (required)
        current_value = self.tree.set(row_id, column=col_name)
        self._edit_entry = ctk.CTkEntry(self.tree, width=width, height=height)
        # Prefill and select text
        self._edit_entry.insert(0, current_value)
        try:
            self._edit_entry.select_range(0, "end")
        except Exception:
            pass

        # place with coordinates only (width/height already provided)
        self._edit_entry.place(x=x, y=y)
        self._edit_entry.focus()

        # Bind events; capture row_id and col_name
        self._edit_entry.bind("<Return>", lambda e, rid=row_id, cname=col_name: self._save_edit(rid, cname))
        self._edit_entry.bind("<FocusOut>", lambda e, rid=row_id, cname=col_name: self._save_edit(rid, cname))

    def _save_edit(self, row_id, col_name):
        if self._edit_entry:
            # Get the new value from the entry widget
            new_value = self._edit_entry.get().strip()  # Strip whitespace from the new value
            if new_value:  # Only update if the new value is not empty
                # Update the Treeview with the new value
                self.tree.set(row_id, column=col_name, value=new_value)
            # Destroy the entry widget
            self._edit_entry.destroy()
            self._edit_entry = None