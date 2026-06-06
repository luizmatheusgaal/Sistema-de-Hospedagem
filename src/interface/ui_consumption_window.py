from tkinter import messagebox, ttk

import customtkinter as ctk

from interface.window_utils import bring_to_front


class ConsumptionWindow(ctk.CTkToplevel):
    def __init__(self, master, service, on_updated):
        super().__init__(master)
        self.service = service
        self.on_updated = on_updated
        self._selected_consumption_id = None

        self.title("Insumos")
        self.geometry("700x500")
        self.update_idletasks()
        self.after(0, lambda: self.state("zoomed"))
        bring_to_front(self, master)

        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(header, text="Cadastro de insumos", font=("Arial", 18, "bold"))
        title.pack(side="left")

        new_button = ctk.CTkButton(header, text="Novo", command=self._clear_form)
        new_button.pack(side="right")

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=(0, 10))

        self.name_entry = ctk.CTkEntry(form, placeholder_text="Nome do insumo")
        self.name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.price_entry = ctk.CTkEntry(form, placeholder_text="Valor (ex: 9.50)")
        self.price_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        save_button = ctk.CTkButton(form, text="Salvar", command=self._save_consumption)
        save_button.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="e")

        delete_button = ctk.CTkButton(
            form,
            text="Excluir",
            fg_color="#B23A3A",
            hover_color="#8F2F2F",
            command=self._delete_consumption,
        )
        delete_button.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")

        self.table = ttk.Treeview(
            self,
            columns=("id", "nome", "valor"),
            show="headings",
        )
        self.table.heading("id", text="ID")
        self.table.heading("nome", text="Nome")
        self.table.heading("valor", text="Valor")
        self.table.column("id", width=50, anchor="center")
        self.table.column("nome", width=220)
        self.table.column("valor", width=120, anchor="center")
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.table.bind("<<TreeviewSelect>>", self._on_select)

        self._load_consumptions()

    def _load_consumptions(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for consumption in self.service.list_consumptions():
            self.table.insert(
                "",
                "end",
                values=(
                    consumption["id"],
                    consumption["name"],
                    f"{float(consumption['price']):.2f}",
                ),
            )

    def _on_select(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return

        values = self.table.item(selection[0], "values")
        self._selected_consumption_id = int(values[0])
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, values[1])
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, values[2])

    def _clear_form(self):
        self._selected_consumption_id = None
        self.name_entry.delete(0, "end")
        self.price_entry.delete(0, "end")

    def _save_consumption(self):
        name = self.name_entry.get().strip()
        price_text = self.price_entry.get().strip().replace(",", ".")

        if not name or not price_text:
            messagebox.showwarning("Dados incompletos", "Informe nome e valor.")
            return

        try:
            price = float(price_text)
        except ValueError:
            messagebox.showwarning("Valor inválido", "Informe um valor válido.")
            return

        if price <= 0:
            messagebox.showwarning("Valor inválido", "Informe um valor maior que zero.")
            return

        try:
            self.service.save_consumption(self._selected_consumption_id, name, price)
        except Exception as exc:
            messagebox.showwarning("Erro", str(exc))
            return

        self._load_consumptions()
        self._clear_form()
        self.on_updated()
        messagebox.showinfo("Insumo salvo", "Insumo atualizado com sucesso.")

    def _delete_consumption(self):
        if self._selected_consumption_id is None:
            messagebox.showwarning("Seleção necessária", "Selecione um insumo para excluir.")
            return

        if not messagebox.askyesno("Confirmar", "Deseja excluir este insumo?"):
            return

        try:
            self.service.delete_consumption(self._selected_consumption_id)
        except Exception as exc:
            messagebox.showwarning("Erro", str(exc))
            return

        self._load_consumptions()
        self._clear_form()
        self.on_updated()
        messagebox.showinfo("Insumo excluído", "Insumo removido com sucesso.")
