import customtkinter as ctk


class ReportFrame(ctk.CTkFrame):
    def __init__(self, master, on_search):
        super().__init__(master)
        self.on_search = on_search

        label = ctk.CTkLabel(self, text="Histórico por data", font=("Arial", 18, "bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))

        self.date_entry = ctk.CTkEntry(self, placeholder_text="DD/MM/AAAA")
        self.date_entry.pack(fill="x", padx=15, pady=5)

        search_button = ctk.CTkButton(self, text="Consultar", command=self._handle_search)
        search_button.pack(fill="x", padx=15, pady=(5, 15))

    def _handle_search(self):
        self.on_search(self.date_entry.get().strip())

    def clear(self):
        self.date_entry.delete(0, "end")
