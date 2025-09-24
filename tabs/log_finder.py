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

        # Configure heading font (unchanged)
        heading_font = tkfont.Font(weight="bold", size=9)
        ttk.Style().configure("Treeview.Heading", font=heading_font)


        self.tree = ttk.Treeview(table_row, columns=("log_folder", "cycle_count", "offset"), show="headings")
        self.tree.heading("log_folder", text="Log Folder", anchor="center")
        self.tree.heading("cycle_count", text="Cycle Count", anchor="center")
        self.tree.heading("offset", text="Offset", anchor="center")
        self.tree.column("log_folder", width=400, anchor="center")  # Center align values
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

        # Ensure logs directory exists and filter to directories only
        try:
            # make dirs to generator
            dirs = (entry.name for entry in os.scandir(LOGS_DIRECTORY) if entry.is_dir())
        except Exception:
            dirs = iter([])

        # Marker to check at end of file
        end_marker = "Bin Results             1(.) 1001(9)"

        matches = ((line, d) for d in dirs for line in lines if d.startswith(line))

        for line, d in matches:
            folder_path = os.path.join(LOGS_DIRECTORY, d)
            try:
                files = (os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))
            except Exception:
                files = []
            cycle_val = "-"
            for fp in files:
                try:
                    # Check file size
                    file_size = os.path.getsize(fp)
                    print(f"Checking file: {fp[0:10]}, size: {file_size} bytes")
                    if file_size > 40000 or file_size < 880:  # Skip files >40KB or <1KB
                        continue

                    with open(fp, "rb") as fh:  # Open in binary mode for reverse reading
                        end_marker_found = False
                        cycle_val = "-"
                        buffer_size = 1024  # Read in chunks of 1KB
                        buffer = b""
                        fh.seek(0, os.SEEK_END)  # Move to the end of the file
                        position = fh.tell()

                        while position > 0:
                            read_size = min(buffer_size, position)
                            position -= read_size
                            fh.seek(position)
                            chunk = fh.read(read_size)
                            buffer = chunk + buffer  # Prepend the chunk to the buffer

                            # Process lines in reverse order
                            lines = buffer.splitlines()
                            buffer = lines.pop(0) if position > 0 else b""  # Keep the incomplete line for the next chunk

                            for line in reversed(lines):
                                line = line.decode(errors="ignore").strip()
                                if not line:
                                    continue

                                if not end_marker_found and line.endswith(end_marker):
                                    end_marker_found = True
                                    continue

                                if end_marker_found and "SELECTED_BLK_COUNT" in line:
                                    cycle_val = line
                                    self.tree.insert("", "end", values=(d, cycle_val, "-"))
                                    break # Exit the for loop

                            if cycle_val != "-":
                                print("break2")
                                break # Exit the while loop
                    if cycle_val != "-":
                        print("break3")
                        break # Exit the for fp in files loop
                except Exception:
                    continue

                self.tree.insert("", "end", values=(d, cycle_val, "-"))

        # Prevent Text widget from inserting a newline when called from a key binding
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
            # Get the new value from the entry widget
            new_value = self._edit_entry.get()
            # Update the Treeview with the new value
            self.tree.set(row_id, column=col_name, value=new_value)
            # Destroy the entry widget
            self._edit_entry.destroy()
            self._edit_entry = None