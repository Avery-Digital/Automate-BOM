import customtkinter as ctk


class ProgressFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(
            self, text="Ready", font=("Arial", 12), anchor="w")
        self.status_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, height=18)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # Stats row
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.found_label = ctk.CTkLabel(
            stats_frame, text="Found: 0", font=("Arial", 12, "bold"),
            text_color="#69DB7C")
        self.found_label.grid(row=0, column=0)

        self.not_found_label = ctk.CTkLabel(
            stats_frame, text="Not Found: 0", font=("Arial", 12, "bold"),
            text_color="#FF6B6B")
        self.not_found_label.grid(row=0, column=1)

        self.skipped_label = ctk.CTkLabel(
            stats_frame, text="Skipped: 0", font=("Arial", 12, "bold"),
            text_color="#FCC419")
        self.skipped_label.grid(row=0, column=2)

        # Log text area
        self.log_text = ctk.CTkTextbox(
            self, font=("Consolas", 11), state="disabled", wrap="word")
        self.log_text.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="nsew")

    def append_log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def update_progress(self, current: int, total: int, part_number: str, status: str):
        if total > 0:
            self.progress_bar.set(current / total)
        self.status_label.configure(
            text=f"Processing {current}/{total}: {part_number}")

    def update_stats(self, found: int, not_found: int, skipped: int):
        self.found_label.configure(text=f"Found: {found}")
        self.not_found_label.configure(text=f"Not Found: {not_found}")
        self.skipped_label.configure(text=f"Skipped: {skipped}")

    def reset(self):
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")
        self.found_label.configure(text="Found: 0")
        self.not_found_label.configure(text="Not Found: 0")
        self.skipped_label.configure(text="Skipped: 0")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def set_complete(self, stats: dict):
        total = stats.get('processed', 0)
        success = stats.get('success', 0)
        rate = (success / total * 100) if total > 0 else 0
        self.status_label.configure(
            text=f"Complete! {success}/{total} parts found ({rate:.0f}% success rate)")
        self.progress_bar.set(1)
