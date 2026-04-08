import customtkinter as ctk
from core.config import load_config, save_config
from core.digikey_api import DigiKeyAPI


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("DigiKey API Settings")
        self.geometry("500x280")
        self.resizable(False, False)

        # Keep on top
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)

        config = load_config()

        # Client ID
        ctk.CTkLabel(self, text="Client ID:", font=("Arial", 13, "bold")).grid(
            row=0, column=0, padx=(20, 10), pady=(25, 8), sticky="w")
        self.client_id_var = ctk.StringVar(value=config['digikey_client_id'])
        self.client_id_entry = ctk.CTkEntry(
            self, textvariable=self.client_id_var, height=32, font=("Arial", 12))
        self.client_id_entry.grid(row=0, column=1, padx=(0, 20), pady=(25, 8), sticky="ew")

        # Client Secret
        ctk.CTkLabel(self, text="Client Secret:", font=("Arial", 13, "bold")).grid(
            row=1, column=0, padx=(20, 10), pady=8, sticky="w")
        self.client_secret_var = ctk.StringVar(value=config['digikey_client_secret'])
        self.client_secret_entry = ctk.CTkEntry(
            self, textvariable=self.client_secret_var, show="*",
            height=32, font=("Arial", 12))
        self.client_secret_entry.grid(row=1, column=1, padx=(0, 20), pady=8, sticky="ew")

        # Status label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 11))
        self.status_label.grid(row=2, column=0, columnspan=2, padx=20, pady=8)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20))

        ctk.CTkButton(btn_frame, text="Test Connection", width=140, height=35,
                       command=self._test, fg_color="#555555",
                       hover_color="#666666").pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Save", width=140, height=35,
                       command=self._save).pack(side="left", padx=8)

    def _test(self):
        self.status_label.configure(text="Testing connection...", text_color="white")
        self.update()

        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()

        if not client_id or not client_secret:
            self.status_label.configure(text="Please enter both Client ID and Secret",
                                        text_color="#FF6B6B")
            return

        api = DigiKeyAPI(client_id, client_secret)
        if api.authenticate():
            self.status_label.configure(text="Connection successful!",
                                        text_color="#69DB7C")
        else:
            self.status_label.configure(text="Connection failed - check credentials",
                                        text_color="#FF6B6B")

    def _save(self):
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()
        save_config(client_id, client_secret)
        self.status_label.configure(text="Saved!", text_color="#69DB7C")
        self.after(1000, self.destroy)
