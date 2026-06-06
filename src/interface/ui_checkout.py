import customtkinter as ctk


class CheckoutFrame(ctk.CTkFrame):
    def __init__(self, master, on_check_out):
        super().__init__(master)
        self.on_check_out = on_check_out

        label = ctk.CTkLabel(self, text="Check-out", font=("Arial", 18, "bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))

        self.room_var = ctk.StringVar(value="-")
        self.room_menu = ctk.CTkOptionMenu(self, variable=self.room_var, values=["-"])
        self.room_menu.pack(fill="x", padx=15, pady=5)

        check_out_button = ctk.CTkButton(
            self, text="Realizar check-out", command=self._handle_check_out
        )
        check_out_button.pack(fill="x", padx=15, pady=10)

    def _handle_check_out(self):
        self.on_check_out(self.room_var.get())

    def set_occupied_rooms(self, values):
        self.room_menu.configure(values=values)
        if self.room_var.get() not in values:
            self.room_var.set(values[0])
