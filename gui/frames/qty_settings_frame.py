import customtkinter as ctk
from core.config import load_config, save_config, DEFAULT_QTY_SETTINGS


class QtySettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring QTY TO BUY settings per component category."""

    CATEGORY_ORDER = ['Resistors', 'Capacitors', 'Ferrite Beads', 'Inductors']

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("QTY TO BUY Settings")
        self.geometry("560x560")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        config = load_config()
        self._qty_settings = config.get('qty_settings', DEFAULT_QTY_SETTINGS)

        # Scrollable container
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        container.grid_columnconfigure((1, 2, 3), weight=1)

        row = 0

        # --- Global overhead section ---
        ctk.CTkLabel(container, text="Global", font=("Arial", 15, "bold")).grid(
            row=row, column=0, columnspan=4, padx=5, pady=(5, 8), sticky="w")
        row += 1

        ctk.CTkLabel(container, text="Overhead %:", font=("Arial", 12)).grid(
            row=row, column=0, padx=(10, 8), pady=4, sticky="w")
        self.overhead_var = ctk.StringVar(
            value=str(self._qty_settings.get('overhead_percent', 10)))
        ctk.CTkEntry(container, textvariable=self.overhead_var, width=70,
                     height=30, font=("Arial", 11)).grid(
            row=row, column=1, padx=4, pady=4, sticky="w")
        ctk.CTkLabel(container, text="added above needed quantity",
                     font=("Arial", 11), text_color="#AAAAAA").grid(
            row=row, column=2, columnspan=2, padx=4, pady=4, sticky="w")
        row += 1

        # Separator
        sep = ctk.CTkFrame(container, height=2, fg_color="#444444")
        sep.grid(row=row, column=0, columnspan=4, padx=5, pady=10, sticky="ew")
        row += 1

        # --- Per-category sections ---
        self._cat_widgets = {}
        categories = self._qty_settings.get('categories', DEFAULT_QTY_SETTINGS['categories'])

        for cat_name in self.CATEGORY_ORDER:
            cat = categories.get(cat_name, DEFAULT_QTY_SETTINGS['categories'].get(cat_name, {}))
            widgets = {}

            # Category header with enable checkbox
            widgets['enabled_var'] = ctk.BooleanVar(value=cat.get('enabled', True))
            ctk.CTkCheckBox(
                container, text=cat_name, variable=widgets['enabled_var'],
                font=("Arial", 14, "bold"), onvalue=True, offvalue=False,
            ).grid(row=row, column=0, columnspan=4, padx=5, pady=(12, 4), sticky="w")
            row += 1

            # Settings row: Step | Max Qty | Max Budget
            labels_frame = ctk.CTkFrame(container, fg_color="transparent")
            labels_frame.grid(row=row, column=0, columnspan=4, padx=20, pady=0, sticky="ew")
            labels_frame.grid_columnconfigure((0, 1, 2), weight=1)

            # Step
            step_frame = ctk.CTkFrame(labels_frame, fg_color="transparent")
            step_frame.grid(row=0, column=0, padx=4, pady=2, sticky="ew")
            ctk.CTkLabel(step_frame, text="Step Size:", font=("Arial", 11)).pack(
                side="left", padx=(0, 4))
            widgets['step_var'] = ctk.StringVar(value=str(cat.get('step', 5)))
            ctk.CTkEntry(step_frame, textvariable=widgets['step_var'], width=60,
                         height=28, font=("Arial", 11)).pack(side="left")

            # Max Qty
            qty_frame = ctk.CTkFrame(labels_frame, fg_color="transparent")
            qty_frame.grid(row=0, column=1, padx=4, pady=2, sticky="ew")
            ctk.CTkLabel(qty_frame, text="Max Qty:", font=("Arial", 11)).pack(
                side="left", padx=(0, 4))
            widgets['max_qty_var'] = ctk.StringVar(value=str(cat.get('max_qty', 1000)))
            ctk.CTkEntry(qty_frame, textvariable=widgets['max_qty_var'], width=60,
                         height=28, font=("Arial", 11)).pack(side="left")

            # Max Budget
            budget_frame = ctk.CTkFrame(labels_frame, fg_color="transparent")
            budget_frame.grid(row=0, column=2, padx=4, pady=2, sticky="ew")
            ctk.CTkLabel(budget_frame, text="Max Budget: $", font=("Arial", 11)).pack(
                side="left", padx=(0, 2))
            widgets['max_budget_var'] = ctk.StringVar(
                value=str(cat.get('max_budget', 25.0)))
            ctk.CTkEntry(budget_frame, textvariable=widgets['max_budget_var'], width=60,
                         height=28, font=("Arial", 11)).pack(side="left")

            self._cat_widgets[cat_name] = widgets
            row += 1

        # --- Status and buttons ---
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 11))
        self.status_label.pack(pady=(4, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(4, 15))

        ctk.CTkButton(btn_frame, text="Reset Defaults", width=120, height=35,
                      command=self._reset_defaults, fg_color="#555555",
                      hover_color="#666666").pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Save", width=120, height=35,
                      command=self._save).pack(side="left", padx=6)

    def _collect_settings(self):
        """Read current widget values into a qty_settings dict."""
        try:
            overhead = float(self.overhead_var.get().strip())
        except (ValueError, TypeError):
            overhead = 10

        categories = {}
        for cat_name, widgets in self._cat_widgets.items():
            try:
                step = int(widgets['step_var'].get().strip())
            except (ValueError, TypeError):
                step = 5
            try:
                max_qty = int(widgets['max_qty_var'].get().strip())
            except (ValueError, TypeError):
                max_qty = 1000
            try:
                max_budget = float(widgets['max_budget_var'].get().strip())
            except (ValueError, TypeError):
                max_budget = 25.0

            categories[cat_name] = {
                'enabled': widgets['enabled_var'].get(),
                'step': max(1, step),
                'max_qty': max(1, max_qty),
                'max_budget': max(0.01, max_budget),
            }

        return {
            'overhead_percent': max(0, overhead),
            'categories': categories,
        }

    def _save(self):
        qty_settings = self._collect_settings()
        config = load_config()
        save_config(
            client_id=config['digikey_client_id'],
            client_secret=config['digikey_client_secret'],
            mouser_api_key=config['mouser_api_key'],
            newark_api_key=config['newark_api_key'],
            qty_settings=qty_settings,
        )
        self.status_label.configure(text="Saved!", text_color="#69DB7C")
        self.after(1000, self.destroy)

    def _reset_defaults(self):
        defaults = DEFAULT_QTY_SETTINGS
        self.overhead_var.set(str(defaults['overhead_percent']))
        for cat_name, widgets in self._cat_widgets.items():
            cat = defaults['categories'].get(cat_name, {})
            widgets['enabled_var'].set(cat.get('enabled', True))
            widgets['step_var'].set(str(cat.get('step', 5)))
            widgets['max_qty_var'].set(str(cat.get('max_qty', 1000)))
            widgets['max_budget_var'].set(str(cat.get('max_budget', 25.0)))
        self.status_label.configure(text="Reset to defaults", text_color="#AAAAAA")
