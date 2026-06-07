import customtkinter as ctk


class ConsumptionFrame(ctk.CTkFrame):
    def __init__(self, master, consumptions, on_consumption):
        super().__init__(master)
        self.on_consumption = on_consumption

        label = ctk.CTkLabel(self, text="🍔 Consumo", font=("Arial", 18, "bold"))
        label.pack(anchor="w", padx=15, pady=(15, 5))

        self.room_var = ctk.StringVar(value="-")
        self.room_menu = ctk.CTkOptionMenu(self, variable=self.room_var, values=["-"])
        self.room_menu.pack(fill="x", padx=15, pady=5)

        values = list(consumptions.keys())
        if not values:
            values = ["-"]
        self.item_var = ctk.StringVar(value=values[0])
        self.item_menu = ctk.CTkOptionMenu(self, variable=self.item_var, values=values)
        self.item_menu.pack(fill="x", padx=15, pady=5)

        self.quantity_entry = ctk.CTkEntry(self, placeholder_text="Quantidade")
        self.quantity_entry.pack(fill="x", padx=15, pady=5)

        consumption_button = ctk.CTkButton(
            self, text="Registrar consumo", command=self._handle_consumption
        )
        consumption_button.pack(fill="x", padx=15, pady=(5, 15))

    def _handle_consumption(self):
        self.on_consumption(
            self.room_var.get(),
            self.item_var.get(),
            self.quantity_entry.get().strip(),
        )

    def set_occupied_rooms(self, values):
        self.room_menu.configure(values=values)
        if self.room_var.get() not in values:
            self.room_var.set(values[0])

    def clear_quantity(self):
        self.quantity_entry.delete(0, "end")

    def set_items(self, values):
        if not values:
            values = ["-"]
        self.item_menu.configure(values=values)
        if self.item_var.get() not in values:
            self.item_var.set(values[0])
