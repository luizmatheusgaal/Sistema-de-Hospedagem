import customtkinter as ctk


class CheckinFrame(ctk.CTkFrame):
    def __init__(self, master, on_check_in):
        super().__init__(master)
        self.on_check_in = on_check_in

        label = ctk.CTkLabel(self, text="🏨 Check-in", font=("Arial", 18, "bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))

        self.guest_name_entry = ctk.CTkEntry(self, placeholder_text="👤 Nome do hóspede")
        self.guest_name_entry.pack(fill="x", padx=15, pady=5)

        self.stay_days_entry = ctk.CTkEntry(self, placeholder_text="📅 Dias de estadia")
        self.stay_days_entry.pack(fill="x", padx=15, pady=5)

        self.room_var = ctk.StringVar(value="-")
        self.room_menu = ctk.CTkOptionMenu(self, variable=self.room_var, values=["-"])
        self.room_menu.pack(fill="x", padx=15, pady=5)

        check_in_button = ctk.CTkButton(
            self, text="Realizar check-in", command=self._handle_check_in
        )
        check_in_button.pack(fill="x", padx=15, pady=(5, 15))

    def _handle_check_in(self):
        self.on_check_in(
            self.guest_name_entry.get().strip(),
            self.stay_days_entry.get().strip(),
            self.room_var.get(),
        )

    def set_available_rooms(self, values):
        self.room_menu.configure(values=values)
        if self.room_var.get() not in values:
            self.room_var.set(values[0])

    def clear(self):
        self.guest_name_entry.delete(0, "end")
        self.stay_days_entry.delete(0, "end")
