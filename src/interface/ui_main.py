from datetime import datetime
import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from interface.ui_checkin import CheckinFrame
from interface.ui_checkout import CheckoutFrame
from interface.ui_consumption import ConsumptionFrame
from interface.ui_consumption_window import ConsumptionWindow
from interface.ui_history_window import HistoryWindow
from interface.ui_room_types_window import RoomTypesWindow
from interface.ui_rooms_window import RoomsWindow
from interface.ui_status import StatusFrame


class MainScreen(ctk.CTkFrame):
    def __init__(self, master, service, on_logout):
        super().__init__(master)
        self.service = service
        self.on_logout = on_logout

        title_label = ctk.CTkLabel(
            self,
            text="Sistema de Gestão da Pousada",
            font=("Arial", 24, "bold"),
        )
        title_label.pack(pady=10)

        intro_label = ctk.CTkLabel(
            self,
            text=(
                "Bem-vindo! Cadastre hóspedes, registre consumos e finalize a estadia pelo menu abaixo."
            ),
        )
        intro_label.pack(pady=5)

        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        actions_frame = ctk.CTkFrame(content_frame)
        actions_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.check_in_frame = CheckinFrame(actions_frame, self._handle_check_in)
        self.check_in_frame.pack(fill="x")
        self.consumption_frame = ConsumptionFrame(
            actions_frame, self.service.consumptions, self._handle_consumption
        )
        self.consumption_frame.pack(fill="x")

        self.check_out_frame = CheckoutFrame(actions_frame, self._handle_check_out)
        self.check_out_frame.pack(fill="x")

        history_button = ctk.CTkButton(
            actions_frame,
            text="Abrir histórico por data",
            command=self._open_history,
        )
        history_button.pack(fill="x", padx=15, pady=(10, 5))

        room_types_button = ctk.CTkButton(
            actions_frame,
            text="Gerenciar tipos de quarto",
            command=self._open_room_types,
        )
        room_types_button.pack(fill="x", padx=15, pady=(0, 5))

        rooms_button = ctk.CTkButton(
            actions_frame,
            text="Cadastrar quarto",
            command=self._open_rooms,
        )
        rooms_button.pack(fill="x", padx=15, pady=(0, 5))

        consumptions_button = ctk.CTkButton(
            actions_frame,
            text="Cadastrar insumo",
            command=self._open_consumptions,
        )
        consumptions_button.pack(fill="x", padx=15, pady=(0, 5))

        close_day_button = ctk.CTkButton(
            actions_frame,
            text="Encerrar expediente",
            fg_color="#B23A3A",
            hover_color="#8F2F2F",
            command=self.close_day,
        )
        close_day_button.pack(fill="x", padx=15, pady=(10, 20))

        self.status_frame = StatusFrame(content_frame)
        self.status_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._history_window = None
        self._room_types_window = None
        self._rooms_window = None
        self._consumptions_window = None

        self.refresh_menus()
        self.refresh_status()
        self.log_message("Sistema iniciado. Pronto para operações.")

    def refresh_menus(self):
        available_rooms = [
            str(room) for room in self.service.rooms if room not in self.service.occupied
        ]
        occupied_rooms = [str(room) for room in self.service.occupied]
        if not available_rooms:
            available_rooms = ["-"]

        if not occupied_rooms:
            occupied_rooms = ["-"]

        self.check_in_frame.set_available_rooms(available_rooms)
        self.consumption_frame.set_occupied_rooms(occupied_rooms)
        self.consumption_frame.set_items(list(self.service.consumptions.keys()))
        self.check_out_frame.set_occupied_rooms(occupied_rooms)

    def refresh_status(self):
        lines = [
            f"Faturamento do dia: R$ {self.service.daily_revenue:.2f}",
            "",
            "Status dos quartos:",
        ]
        for room_number in self.service.rooms:
            if room_number in self.service.occupied:
                guest_name = self.service.occupied[room_number]["guest_name"]
                room_type = self.service.get_room_type(room_number)
                lines.append(
                    f"Quarto {room_number} ({room_type}): OCUPADO ({guest_name})"
                )
            else:
                room_type = self.service.get_room_type(room_number)
                lines.append(f"Quarto {room_number} ({room_type}): LIVRE")
        self.status_frame.update_status("\n".join(lines) + "\n")

    def log_message(self, message):
        self.status_frame.append_log(message)

    def _handle_check_in(self, guest_name, stay_days_text, room_text):
        if room_text == "-":
            messagebox.showwarning("Dados incompletos", "Escolha um quarto disponível.")
            return
        if not stay_days_text.isdigit():
            messagebox.showwarning("Dias inválidos", "Informe um número de dias válido.")
            return

        stay_days = int(stay_days_text)
        room_number = int(room_text)
        try:
            reservation_code = self.service.check_in(guest_name, stay_days, room_number)
        except ValueError as exc:
            messagebox.showwarning("Check-in", str(exc))
            return

        self.check_in_frame.clear()
        self.log_message(
            f"Check-in realizado: {guest_name} no quarto {room_number} ({reservation_code})."
        )
        self.refresh_menus()
        self.refresh_status()

    def _handle_consumption(self, room_text, item, quantity_text):
        if room_text == "-":
            messagebox.showwarning("Dados incompletos", "Selecione um quarto ocupado.")
            return
        if not quantity_text.isdigit():
            messagebox.showwarning("Quantidade inválida", "Informe uma quantidade válida.")
            return

        room_number = int(room_text)
        quantity = int(quantity_text)
        try:
            amount = self.service.record_consumption(room_number, item, quantity)
        except ValueError as exc:
            messagebox.showwarning("Consumo", str(exc))
            return

        self.consumption_frame.clear_quantity()
        self.log_message(
            f"Consumo registrado no quarto {room_number}: {item} x{quantity} = R$ {amount:.2f}."
        )
        self.refresh_status()

    def _handle_check_out(self, room_text):
        if room_text == "-":
            messagebox.showwarning("Sem ocupação", "Não há quartos ocupados.")
            return

        room_number = int(room_text)
        try:
            total, stay_data = self.service.check_out(room_number)
        except ValueError as exc:
            messagebox.showwarning("Check-out", str(exc))
            return

        self.log_message(
            f"Check-out realizado: {stay_data['guest_name']} (quarto {room_number}) - Total R$ {total:.2f}."
        )
        self.refresh_menus()
        self.refresh_status()

    def _open_history(self):
        if self._history_window and self._history_window.winfo_exists():
            self._history_window.focus()
            return

        self._history_window = HistoryWindow(self.master, self.service)

    def _open_room_types(self):
        if self._room_types_window and self._room_types_window.winfo_exists():
            self._room_types_window.focus()
            return

        self._room_types_window = RoomTypesWindow(
            self.master, self.service, self.refresh_status
        )

    def _open_rooms(self):
        if self._rooms_window and self._rooms_window.winfo_exists():
            self._rooms_window.focus()
            return

        self._rooms_window = RoomsWindow(self.master, self.service, self._refresh_after_room)

    def _open_consumptions(self):
        if self._consumptions_window and self._consumptions_window.winfo_exists():
            self._consumptions_window.focus()
            return

        self._consumptions_window = ConsumptionWindow(
            self.master, self.service, self._refresh_after_consumption
        )

    def _refresh_after_consumption(self):
        self.refresh_menus()

    def _refresh_after_room(self):
        self.refresh_menus()
        self.refresh_status()

    def close_day(self):
        data = datetime.now().strftime("%Y%m%d_%H%M")
        default_report_path = os.path.join(
            os.path.dirname(__file__), f"../report/relatorio_fechamento_{data}.txt"
        )
        if not messagebox.askyesno("Encerrar expediente", "Deseja sair?"):
            return

        report_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Relatório", "*.txt")],
            initialfile=os.path.basename(default_report_path),
            initialdir=os.path.dirname(default_report_path),
            title="Salvar relatório",
        )
        if not report_path:
            return

        self.service.generate_report(report_path)
        messagebox.showinfo("Fechamento concluído", f"Relatório salvo em {report_path}")
        self.destroy()
        self.on_logout()
