from tkinter import messagebox, ttk

import customtkinter as ctk

from interface.window_utils import bring_to_front


class RoomTypesWindow(ctk.CTkToplevel):
    def __init__(self, master, service, on_updated):
        super().__init__(master)
        self.service = service
        self.on_updated = on_updated
        self._selected_room_type_id = None

        self.title("Tipos de Quarto")
        self.geometry("700x500")
        bring_to_front(self, master)

        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(header, text="Gerenciar tipos", font=("Arial", 18, "bold"))
        title.pack(side="left")

        new_button = ctk.CTkButton(header, text="Novo", command=self._clear_form)
        new_button.pack(side="right")

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=(0, 10))

        self.name_entry = ctk.CTkEntry(form, placeholder_text="Nome do tipo")
        self.name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.description_entry = ctk.CTkEntry(form, placeholder_text="Descrição")
        self.description_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.daily_rate_entry = ctk.CTkEntry(form, placeholder_text="Valor da diária")
        self.daily_rate_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=2)
        form.grid_columnconfigure(2, weight=1)

        save_button = ctk.CTkButton(form, text="Salvar", command=self._save_room_type)
        save_button.grid(row=1, column=2, padx=5, pady=(0, 5), sticky="e")

        self.table = ttk.Treeview(
            self,
            columns=("id", "nome", "descricao", "valor"),
            show="headings",
        )
        self.table.heading("id", text="ID")
        self.table.heading("nome", text="Nome")
        self.table.heading("descricao", text="Descrição")
        self.table.heading("valor", text="Diária")
        self.table.column("id", width=50, anchor="center")
        self.table.column("nome", width=140)
        self.table.column("descricao", width=280)
        self.table.column("valor", width=90, anchor="e")
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.table.bind("<<TreeviewSelect>>", self._on_select)

        self._load_room_types()

    def _load_room_types(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for room_type in self.service.list_room_types():
            self.table.insert(
                "",
                "end",
                values=(
                    room_type["id"],
                    room_type["name"],
                    room_type["description"],
                    f"R$ {float(room_type['daily_rate']):.2f}",
                ),
            )

    def _on_select(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return

        values = self.table.item(selection[0], "values")
        self._selected_room_type_id = int(values[0])
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])
        self.description_entry.delete(0, "end")
        self.description_entry.insert(0, values[2])
        self.daily_rate_entry.delete(0, "end")
        self.daily_rate_entry.insert(0, values[3].replace("R$ ", ""))

    def _clear_form(self):
        self._selected_room_type_id = None
        self.name_entry.delete(0, "end")
        self.description_entry.delete(0, "end")
        self.daily_rate_entry.delete(0, "end")

    def _save_room_type(self):
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        daily_rate_text = self.daily_rate_entry.get().replace(",", ".").strip()

        if not name or not description or not daily_rate_text:
            messagebox.showwarning("Dados incompletos", "Preencha todos os campos.")
            return

        try:
            daily_rate = float(daily_rate_text)
        except ValueError:
            messagebox.showwarning("Valor inválido", "Informe um valor numérico válido.")
            return

        self.service.save_room_type(
            self._selected_room_type_id, name, description, daily_rate
        )
        self.service.refresh_room_types()
        self._load_room_types()
        self._clear_form()
        self.on_updated()
        messagebox.showinfo("Tipo salvo", "Tipo de quarto atualizado com sucesso.")
