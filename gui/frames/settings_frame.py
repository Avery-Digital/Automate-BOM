import customtkinter as ctk
from core.config import load_config, save_config
from core.digikey_api import DigiKeyAPI
from core.mouser_api import MouserAPI
from core.newark_api import NewarkAPI


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("API Settings")
        self.geometry("520x480")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)

        config = load_config()

        # DigiKey section
        ctk.CTkLabel(self, text="DigiKey", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        ctk.CTkLabel(self, text="Client ID:", font=("Arial", 12)).grid(
            row=1, column=0, padx=(20, 10), pady=4, sticky="w")
        self.client_id_var = ctk.StringVar(value=config['digikey_client_id'])
        ctk.CTkEntry(self, textvariable=self.client_id_var, height=30,
                     font=("Arial", 11)).grid(row=1, column=1, padx=(0, 20), pady=4, sticky="ew")

        ctk.CTkLabel(self, text="Client Secret:", font=("Arial", 12)).grid(
            row=2, column=0, padx=(20, 10), pady=4, sticky="w")
        self.client_secret_var = ctk.StringVar(value=config['digikey_client_secret'])
        ctk.CTkEntry(self, textvariable=self.client_secret_var, show="*", height=30,
                     font=("Arial", 11)).grid(row=2, column=1, padx=(0, 20), pady=4, sticky="ew")

        # Mouser section
        ctk.CTkLabel(self, text="Mouser", font=("Arial", 14, "bold")).grid(
            row=3, column=0, columnspan=2, padx=20, pady=(12, 5), sticky="w")

        ctk.CTkLabel(self, text="API Key:", font=("Arial", 12)).grid(
            row=4, column=0, padx=(20, 10), pady=4, sticky="w")
        self.mouser_key_var = ctk.StringVar(value=config['mouser_api_key'])
        ctk.CTkEntry(self, textvariable=self.mouser_key_var, show="*", height=30,
                     font=("Arial", 11)).grid(row=4, column=1, padx=(0, 20), pady=4, sticky="ew")

        # Newark section
        ctk.CTkLabel(self, text="Newark", font=("Arial", 14, "bold")).grid(
            row=5, column=0, columnspan=2, padx=20, pady=(12, 5), sticky="w")

        ctk.CTkLabel(self, text="API Key:", font=("Arial", 12)).grid(
            row=6, column=0, padx=(20, 10), pady=4, sticky="w")
        self.newark_key_var = ctk.StringVar(value=config['newark_api_key'])
        ctk.CTkEntry(self, textvariable=self.newark_key_var, show="*", height=30,
                     font=("Arial", 11)).grid(row=6, column=1, padx=(0, 20), pady=4, sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 11))
        self.status_label.grid(row=7, column=0, columnspan=2, padx=20, pady=6)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=(5, 15))

        ctk.CTkButton(btn_frame, text="Test DigiKey", width=105, height=35,
                       command=self._test_digikey, fg_color="#555555",
                       hover_color="#666666").pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Test Mouser", width=105, height=35,
                       command=self._test_mouser, fg_color="#555555",
                       hover_color="#666666").pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Test Newark", width=105, height=35,
                       command=self._test_newark, fg_color="#555555",
                       hover_color="#666666").pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="Save", width=105, height=35,
                       command=self._save).pack(side="left", padx=4)

    def _test_digikey(self):
        self.status_label.configure(text="Testing DigiKey...", text_color="white")
        self.update()
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        if not client_id or not client_secret:
            self.status_label.configure(text="Enter DigiKey credentials", text_color="#FF6B6B")
            return
        api = DigiKeyAPI(client_id, client_secret)
        if api.authenticate():
            self.status_label.configure(text="DigiKey OK!", text_color="#69DB7C")
        else:
            self.status_label.configure(text="DigiKey failed", text_color="#FF6B6B")

    def _test_mouser(self):
        self.status_label.configure(text="Testing Mouser...", text_color="white")
        self.update()
        api_key = self.mouser_key_var.get().strip()
        if not api_key:
            self.status_label.configure(text="Enter Mouser API Key", text_color="#FF6B6B")
            return
        api = MouserAPI(api_key)
        result = api.search_part("RC0805FR-070RL")
        if result and result.get('SearchResults', {}).get('Parts'):
            self.status_label.configure(text="Mouser OK!", text_color="#69DB7C")
        else:
            self.status_label.configure(text="Mouser failed", text_color="#FF6B6B")

    def _test_newark(self):
        self.status_label.configure(text="Testing Newark...", text_color="white")
        self.update()
        api_key = self.newark_key_var.get().strip()
        if not api_key:
            self.status_label.configure(text="Enter Newark API Key", text_color="#FF6B6B")
            return
        api = NewarkAPI(api_key)
        result = api.search_part("RC0805FR-070RL")
        if result and result.get('manufacturerPartNumberSearchReturn', {}).get('products'):
            self.status_label.configure(text="Newark OK!", text_color="#69DB7C")
        else:
            self.status_label.configure(text="Newark failed", text_color="#FF6B6B")

    def _save(self):
        save_config(
            self.client_id_var.get().strip(),
            self.client_secret_var.get().strip(),
            self.mouser_key_var.get().strip(),
            self.newark_key_var.get().strip(),
        )
        self.status_label.configure(text="Saved!", text_color="#69DB7C")
        self.after(1000, self.destroy)
