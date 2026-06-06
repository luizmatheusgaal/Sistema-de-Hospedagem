import customtkinter as ctk

class StatusFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        status_label = ctk.CTkLabel(
            self, text="Status & Relatórios", font=("Arial", 18, "bold")
        )
        status_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.status_textbox = ctk.CTkTextbox(self, height=220)
        self.status_textbox.pack(fill="x", padx=15, pady=5)
        self.status_textbox.configure(state="disabled")

        log_label = ctk.CTkLabel(self, text="Movimentações", font=("Arial", 18, "bold"))
        log_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.log_textbox = ctk.CTkTextbox(self)
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log_textbox.configure(state="disabled")


    def update_status(self, text):
        self.status_textbox.configure(state="normal")
        self.status_textbox.delete("1.0", "end")
        self.status_textbox.insert("end", text)
        self.status_textbox.configure(state="disabled")

    def append_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

