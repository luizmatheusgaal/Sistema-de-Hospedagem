from tkinter import messagebox, ttk

import customtkinter as ctk

from interface.window_utils import bring_to_front


class RoomsWindow(ctk.CTkToplevel):
    def __init__(self, master, service, on_updated):
        super().__init__(master)
        self.service = service
        self.on_updated = on_updated
        self._selected_room_id = None

        self.title("Quartos")
        self.geometry("700x500")
        self.update_idletasks()
        self.after(0, lambda: self.state("zoomed"))
        bring_to_front(self, master)

        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(header, text="Gerenciar quartos", font=("Arial", 18, "bold"))
        title.pack(side="left")

        new_button = ctk.CTkButton(header, text="Novo", command=self._clear_form)
        new_button.pack(side="right")

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=(0, 10))

        self.room_number_entry = ctk.CTkEntry(form, placeholder_text="Número do quarto")
        self.room_number_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.room_type_var = ctk.StringVar(value="-")
        self.room_type_menu = ctk.CTkOptionMenu(
            form, variable=self.room_type_var, values=["-"]
        )
        self.room_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        save_button = ctk.CTkButton(form, text="Salvar", command=self._save_room)
        save_button.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="e")

        delete_button = ctk.CTkButton(
            form,
            text="Excluir",
            fg_color="#B23A3A",
            hover_color="#8F2F2F",
            command=self._delete_room,
        )
        delete_button.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")

        self.table = ttk.Treeview(
            self,
            columns=("id", "numero", "tipo"),
            show="headings",
        )
        self.table.heading("id", text="ID")
        self.table.heading("numero", text="Número")
        self.table.heading("tipo", text="Tipo")
        self.table.column("id", width=50, anchor="center")
        self.table.column("numero", width=120, anchor="center")
        self.table.column("tipo", width=200)
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.table.bind("<<TreeviewSelect>>", self._on_select)

        self._load_room_types()
        self._load_rooms()

    def _load_room_types(self):
        room_types = self.service.list_room_types()
        self._room_type_map = {room_type["name"]: room_type["id"] for room_type in room_types}
        names = [room_type["name"] for room_type in room_types]
        if not names:
            names = ["-"]
        self.room_type_menu.configure(values=names)
        if self.room_type_var.get() not in names:
            self.room_type_var.set(names[0])

    def _load_rooms(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for room in self.service.list_rooms_with_type():
            self.table.insert(
                "",
                "end",
                values=(
                    room["id"],
                    room["room_number"],
                    room["room_type_name"],
                ),
            )

    def _on_select(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return

        values = self.table.item(selection[0], "values")
        self._selected_room_id = int(values[0])
        self.room_number_entry.delete(0, "end")
        self.room_number_entry.insert(0, values[1])
        self.room_number_entry.configure(state="disabled")
        self.room_type_var.set(values[2])

    def _clear_form(self):
        self._selected_room_id = None
        self.room_number_entry.configure(state="normal")
        self.room_number_entry.delete(0, "end")
        self.room_type_var.set("-")

    def _save_room(self):
        room_number_text = self.room_number_entry.get().strip()
        room_type_name = self.room_type_var.get()

        if not room_number_text or room_type_name == "-":
            messagebox.showwarning("Dados incompletos", "Informe número e tipo.")
            return
        if not room_number_text.isdigit():
            messagebox.showwarning("Número inválido", "Informe um número válido.")
            return

        room_type_id = self._room_type_map.get(room_type_name)
        if not room_type_id:
            messagebox.showwarning("Tipo inválido", "Selecione um tipo válido.")
            return

        room_number = int(room_number_text)
        try:
            if self._selected_room_id is None:
                self.service.create_room(room_number, room_type_id)
            else:
                self.service.update_room_type_for_room(self._selected_room_id, room_type_id)
        except Exception as exc:
            messagebox.showwarning("Erro", str(exc))
            return

        self._load_rooms()
        self._clear_form()
        self.on_updated()
        messagebox.showinfo("Quarto salvo", "Quarto atualizado com sucesso.")

    def _delete_room(self):
        if self._selected_room_id is None:
            messagebox.showwarning("Seleção necessária", "Selecione um quarto para excluir.")
            return

        if not messagebox.askyesno("Confirmar", "Deseja excluir este quarto?"):
            return

        room_number_text = self.room_number_entry.get().strip()
        try:
            self.service.delete_room(self._selected_room_id, int(room_number_text))
        except Exception as exc:
            messagebox.showwarning("Erro", str(exc))
            return

        self._load_rooms()
        self._clear_form()
        self.on_updated()
        messagebox.showinfo("Quarto excluído", "Quarto removido com sucesso.")
