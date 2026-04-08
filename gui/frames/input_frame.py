import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime


class InputFrame(ctk.CTkFrame):
    def __init__(self, master, on_settings_click=None, **kwargs):
        super().__init__(master, **kwargs)
        self._on_settings = on_settings_click

        self.grid_columnconfigure(1, weight=1)

        row = 0

        # BOM Name
        ctk.CTkLabel(self, text="BOM Name:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=(15, 5), sticky="w")
        self.bom_name_var = ctk.StringVar()
        self.bom_name_entry = ctk.CTkEntry(
            self, textvariable=self.bom_name_var,
            placeholder_text="Enter BOM name (used for title and output filename)",
            height=32, font=("Arial", 12))
        self.bom_name_entry.grid(row=row, column=1, padx=(0, 8), pady=(15, 5), sticky="ew")

        # Settings button
        self.settings_btn = ctk.CTkButton(
            self, text="Settings", width=90, height=32, command=self._on_settings,
            fg_color="#555555", hover_color="#666666")
        self.settings_btn.grid(row=row, column=2, padx=(0, 15), pady=(15, 5))

        row += 1

        # Date
        ctk.CTkLabel(self, text="Date:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=5, sticky="w")
        self.date_label = ctk.CTkLabel(
            self, text=datetime.now().strftime('%m/%d/%Y'),
            font=("Arial", 12))
        self.date_label.grid(row=row, column=1, padx=(0, 8), pady=5, sticky="w")

        row += 1

        # Input Mode
        ctk.CTkLabel(self, text="Input Mode:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=5, sticky="w")
        self.mode_var = ctk.StringVar(value="Excel BOM")
        self.mode_selector = ctk.CTkSegmentedButton(
            self, values=["Excel BOM", "Altium BOM", "Part Number List"],
            variable=self.mode_var, command=self._on_mode_change,
            font=("Arial", 12))
        self.mode_selector.grid(row=row, column=1, columnspan=2, padx=(0, 15), pady=5, sticky="ew")

        row += 1

        # Distributor
        ctk.CTkLabel(self, text="Distributor:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=5, sticky="w")
        self.distributor_var = ctk.StringVar(value="DigiKey")
        self.distributor_selector = ctk.CTkOptionMenu(
            self, values=["DigiKey", "Mouser", "Newark",
                          "DigiKey 1st", "Mouser 1st", "Newark 1st"],
            variable=self.distributor_var,
            font=("Arial", 12), height=32, width=200)
        self.distributor_selector.grid(row=row, column=1, columnspan=2, padx=(0, 15), pady=5, sticky="ew")

        row += 1

        # Number of Boards
        ctk.CTkLabel(self, text="# of Boards:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=5, sticky="w")
        self.num_boards_var = ctk.StringVar(value="1")
        self.num_boards_entry = ctk.CTkEntry(
            self, textvariable=self.num_boards_var, width=80,
            height=32, font=("Arial", 12))
        self.num_boards_entry.grid(row=row, column=1, padx=(0, 8), pady=5, sticky="w")
        ctk.CTkLabel(self, text="(optional, defaults to 1)", font=("Arial", 11),
                     text_color="#AAAAAA").grid(row=row, column=1, padx=(100, 0), pady=5, sticky="w")

        row += 1

        # File Browser
        ctk.CTkLabel(self, text="Input File:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, padx=(15, 8), pady=(5, 15), sticky="w")
        self.file_var = ctk.StringVar()
        self.file_entry = ctk.CTkEntry(
            self, textvariable=self.file_var, state="readonly",
            height=32, font=("Arial", 11))
        self.file_entry.grid(row=row, column=1, padx=(0, 8), pady=(5, 15), sticky="ew")

        self.browse_btn = ctk.CTkButton(
            self, text="Browse", width=90, height=32, command=self._browse)
        self.browse_btn.grid(row=row, column=2, padx=(0, 15), pady=(5, 15))

    def _on_mode_change(self, value):
        # Clear file selection when mode changes
        self.file_var.set("")

    def _browse(self):
        mode = self.mode_var.get()
        if mode == "Excel BOM":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        elif mode == "Altium BOM":
            filetypes = [("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        else:  # Part Number List
            filetypes = [("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]

        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.file_var.set(path)

    def get_inputs(self):
        num_boards = self.num_boards_var.get().strip()
        try:
            num_boards = int(num_boards) if num_boards else 1
        except ValueError:
            num_boards = 1
        return {
            'bom_name': self.bom_name_var.get().strip(),
            'mode': self.mode_var.get(),
            'file_path': self.file_var.get().strip(),
            'num_boards': num_boards,
            'distributor': self.distributor_var.get(),
        }
