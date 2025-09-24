import customtkinter as ctk
from tkinter import ttk, font as tkfont
import os

LOGS_DIRECTORY = R"C:\Users\gohzu\Desktop\pwlrx_tkinter_minimalVibe\n69r"

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
        heading_font = tkfont.Font(weight="bold", size=12)
        ttk.Style().configure("Treeview.Heading", font=heading_font)
        font = tkfont.Font(size= 9)
        ttk.Style().configure("Treeview", font=font)
        self.tree = ttk.Treeview(table_row, columns=("lot_id", "cycle_count", "offset"), show="headings")
        self.tree.heading("lot_id", text="Lot ID")
        self.tree.heading("cycle_count", text="Cycle Count")
        self.tree.heading("offset", text="Offset")
        self.tree.pack(fill="both", expand=True)

        self._edit_entry = None
        self.tree.bind("<Double-1>", self._on_double_click)

    # accept optional event so this can be used as a key binding callback
    def _search_logs(self, event=None):
        # Clear previous results
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # Get input lines
        raw_text = self.textbox.get("1.0", "end")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        # Ensure logs directory exists
        try:
            entries = os.listdir(LOGS_DIRECTORY)
        except Exception:
            entries = []

        # Filter to directories only
        dirs = [name for name in entries if os.path.isdir(os.path.join(LOGS_DIRECTORY, name))]

        for line in lines:
            matches = [d for d in dirs if d.startswith(line)]
            if matches:
                for m in matches:
                    # insert folder name; placeholder values for other columns
                    self.tree.insert("", "end", values=(m, "0", "-"))
            else:
                # indicate not found for this query
                self.tree.insert("", "end", values=(line, "Not found", "-"))

        # when called from a key binding, prevent the Text widget from inserting a newline
        if event is not None:
            return "break"

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
            new_value = self._edit_entry.get()
            # Use the column name (not "#1") when setting the value
            self.tree.set(row_id, column=col_name, value=new_value)
            self._edit_entry.destroy()
            self._edit_entry = None
