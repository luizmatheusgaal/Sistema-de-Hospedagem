import csv
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from interface.window_utils import bring_to_front


class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, master, service):
        super().__init__(master)
        self.service = service
        self._current_history = []

        self.title("Histórico por Data")
        self.geometry("700x500")
        self.update_idletasks()
        self.after(0, lambda: self.state("zoomed"))
        bring_to_front(self, master)

        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=(20, 10))

        label = ctk.CTkLabel(header, text="Consultar histórico", font=("Arial", 18, "bold"))
        label.pack(side="left")

        self.date_entry = ctk.CTkEntry(header, placeholder_text="DD/MM/AAAA")
        self.date_entry.pack(side="left", padx=10)

        self.guest_entry = ctk.CTkEntry(header, placeholder_text="Hóspede")
        self.guest_entry.pack(side="left", padx=5)

        self.room_entry = ctk.CTkEntry(header, placeholder_text="Quarto")
        self.room_entry.pack(side="left", padx=5)

        search_button = ctk.CTkButton(header, text="Consultar", command=self._search_history)
        search_button.pack(side="left", padx=5)

        clear_button = ctk.CTkButton(header, text="Limpar filtros", command=self._clear_filters)
        clear_button.pack(side="left", padx=5)

        export_button = ctk.CTkButton(header, text="Exportar CSV", command=self._export_csv)
        export_button.pack(side="right")

        self.table = ttk.Treeview(
            self,
            columns=("quarto", "tipo", "nome", "dias", "consumo", "total", "checkout"),
            show="headings",
        )
        self.table.heading("quarto", text="Quarto")
        self.table.heading("tipo", text="Tipo")
        self.table.heading("nome", text="Hóspede")
        self.table.heading("dias", text="Dias")
        self.table.heading("consumo", text="Consumo")
        self.table.heading("total", text="Total")
        self.table.heading("checkout", text="Checkout")
        self.table.column("quarto", width=80, anchor="center")
        self.table.column("tipo", width=100)
        self.table.column("nome", width=180)
        self.table.column("dias", width=60, anchor="center")
        self.table.column("consumo", width=90, anchor="e")
        self.table.column("total", width=90, anchor="e")
        self.table.column("checkout", width=90, anchor="center")
        self.table.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _search_history(self):
        date_text = self.date_entry.get().strip()
        try:
            reference_date = datetime.strptime(date_text, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showwarning("Data inválida", "Use o formato DD/MM/AAAA.")
            return

        history = self.service.fetch_history_by_date(reference_date)
        guest_filter = self.guest_entry.get().strip().lower()
        room_text = self.room_entry.get().strip()
        room_filter = None

        if room_text:
            if not room_text.isdigit():
                messagebox.showwarning("Quarto inválido", "Informe apenas números no quarto.")
                return
            room_filter = int(room_text)

        if guest_filter:
            history = [
                item
                for item in history
                if guest_filter in item["guest_name"].lower()
            ]
        if room_filter is not None:
            history = [item for item in history if item["room_number"] == room_filter]

        self._current_history = history
        for item in self.table.get_children():
            self.table.delete(item)

        if not history:
            messagebox.showinfo("Sem registros", "Nenhum checkout encontrado para os filtros.")
            return

        for item in history:
            self.table.insert(
                "",
                "end",
                values=(
                    item["room_number"],
                    item.get("room_type_name", "-"),
                    item["guest_name"],
                    item["days"],
                    f"R$ {float(item['consumption']):.2f}",
                    f"R$ {float(item['total']):.2f}",
                    item["checkout"].strftime("%H:%M"),
                ),
            )

    def _clear_filters(self):
        self.date_entry.delete(0, "end")
        self.guest_entry.delete(0, "end")
        self.room_entry.delete(0, "end")
        self._current_history = []
        for item in self.table.get_children():
            self.table.delete(item)

    def _export_csv(self):
        if not self._current_history:
            messagebox.showwarning("Exportar CSV", "Nenhum histórico carregado.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar relatório CSV",
        )
        if not filepath:
            return

        with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(
                ["Quarto", "Tipo", "Hóspede", "Dias", "Consumo", "Total", "Checkout"]
            )
            for item in self._current_history:
                writer.writerow(
                    [
                        item["room_number"],
                        item.get("room_type_name", "-"),
                        item["guest_name"],
                        item["days"],
                        f"{float(item['consumption']):.2f}",
                        f"{float(item['total']):.2f}",
                        item["checkout"].strftime("%H:%M"),
                    ]
                )

        messagebox.showinfo("Exportar CSV", f"Arquivo salvo em {filepath}.")
