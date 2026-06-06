from datetime import datetime
import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from interface.ui_checkin import CheckinFrame
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
        self.refresh_menus()
        self.status_frame.append_log("Sistema iniciado. Pronto para operações.")

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
        self.status_frame.append_log(
            f"Check-in realizado: {guest_name} no quarto {room_number} ({reservation_code})."
        )
        self.refresh_menus()

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

        self.status_frame.append_log(
            f"Check-out realizado: {stay_data['guest_name']} (quarto {room_number}) - Total R$ {total:.2f}."
        )
        self.refresh_menus()

    def _refresh_after_room(self):
        self.refresh_menus()

    def close_day(self):
        if not messagebox.askyesno("Encerrar expediente", "Deseja sair?"):
            return

        self.destroy()
        self.on_logout()
