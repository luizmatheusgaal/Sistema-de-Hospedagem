import os
import random
from datetime import datetime

from db import DatabaseManager
from dotenv import load_dotenv

load_dotenv()


class LodgingService:
    def __init__(self):
        self.rooms = [101 + i for i in range(int(os.getenv("LIMITE_QUARTOS", "10")))]
        self.occupied = {}
        self.history = []
        self.daily_revenue = 0.0
        self.db = DatabaseManager()
        self.db.create_tables()
        self._load_data()
        self.consumptions = self._load_consumptions()

    def _load_data(self):
        self.rooms_info = {
            item["room_number"]: {
                "room_type_id": item["room_type_id"],
                "room_type_name": item["room_type_name"],
                "daily_rate": float(item["daily_rate"]),
            }
            for item in self.db.load_rooms_with_type()
        }
        self.occupied.clear()
        for item in self.db.load_occupancies():
            self.occupied[item["room_number"]] = {
                "guest_name": item["guest_name"],
                "days": item["days"],
                "checkin": item["checkin"],
                "consumption": float(item["consumption"]),
                "reservation": item["reservation"],
            }
        self.history = list(self.db.load_history())
        self.daily_revenue = self.db.calculate_daily_revenue(
            datetime.now().date()
        )

    def _load_consumptions(self):
        consumptions = self.db.list_consumptions()
        return {item["name"]: float(item["price"]) for item in consumptions}

    def generate_reservation_code(self):
        return f"RES-{random.randint(1000, 9999)}"

    def check_in(self, guest_name, stay_days, room_number):
        if not guest_name:
            raise ValueError("Informe o nome do hóspede.")

        if stay_days <= 0:
            raise ValueError("Informe um número de dias válido.")

        if room_number not in self.rooms:
            raise ValueError("Quarto inválido.")

        if room_number in self.occupied:
            raise ValueError("Quarto já está ocupado.")

        reservation_code = self.generate_reservation_code()
        checkin_time = datetime.now()
        self.occupied[room_number] = {
            "guest_name": guest_name,
            "days": stay_days,
            "checkin": checkin_time,
            "consumption": 0.0,
            "reservation": reservation_code,
        }
        self.db.insert_checkin(room_number, guest_name, stay_days, checkin_time, reservation_code)
        return reservation_code

    def record_consumption(self, room_number, item, quantity):
        if room_number not in self.occupied:
            raise ValueError("Selecione um quarto ocupado.")

        if item not in self.consumptions:
            raise ValueError("Selecione um item válido.")

        if quantity <= 0:
            raise ValueError("Informe uma quantidade válida.")

        amount = self.consumptions[item] * quantity
        self.occupied[room_number]["consumption"] += amount
        self.db.add_consumption(room_number, amount)
        return amount

    def check_out(self, room_number):
        stay_data = self.occupied.get(room_number)
        if not stay_data:
            raise ValueError("Selecione um quarto ocupado.")

        daily_rate = self.rooms_info.get(room_number, {}).get(
            "daily_rate", float(os.getenv("VALOR_DIARIA", "150.00"))
        )
        room_total = stay_data["days"] * daily_rate
        total = room_total + stay_data["consumption"]

        self.db.finalize_checkout(
            room_number,
            stay_data["consumption"],
            total,
            stay_data["reservation"],
            stay_data["guest_name"],
            stay_data["days"],
            stay_data["checkin"],
        )
        self.db.add_daily_revenue(datetime.now().date(), total)

        history_item = {
            "room": room_number,
            "guest_name": stay_data["guest_name"],
            "days": stay_data["days"],
            "consumption": stay_data["consumption"],
            "total": total,
            "reservation": stay_data["reservation"],
            "checkout": datetime.now(),
        }
        self.history.append(history_item)
        self.daily_revenue = self.db.calculate_daily_revenue(
            datetime.now().date()
        )

        del self.occupied[room_number]
        return total, stay_data

    def generate_report(self, filepath):
        self.history = list(self.db.load_history())
        self.daily_revenue = self.db.calculate_daily_revenue(
            datetime.now().date()
        )

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        lines = [
            "Relatório de fechamento - Pousada\n",
            f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n",
            f"Faturamento total: R$ {self.daily_revenue:.2f}\n",
            "\nHistórico de hospedagens:\n",
        ]

        if not self.history:
            lines.append("Nenhuma hospedagem finalizada.\n")

        else:
            for item in self.history:
                room_number = item.get("room", item.get("room_number"))
                guest_name = item.get("guest_name", item.get("nome"))
                stay_days = item.get("days", item.get("dias"))
                consumption = item.get("consumption", item.get("consumo"))
                reservation = item.get("reservation", item.get("reserva"))
                lines.append(
                    "- Quarto {quarto} | Hóspede: {nome} | Dias: {dias} | Consumo: R$ {consumo:.2f} | "
                    "Total: R$ {total:.2f} | Reserva: {reserva} | Checkout: {checkout}\n".format(
                        quarto=room_number,
                        nome=guest_name,
                        dias=stay_days,
                        consumo=float(consumption),
                        total=float(item["total"]),
                        reserva=reservation,
                        checkout=item["checkout"].strftime("%d/%m/%Y %H:%M"),
                    )
                )

        if self.occupied:
            lines.append("\nQuartos ainda ocupados:\n")
            for room_number, stay_data in self.occupied.items():
                lines.append(
                    f"- Quarto {room_number} | Hóspede: {stay_data['guest_name']} | "
                    f"Reserva: {stay_data['reservation']}\n"
                )

        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def fetch_history_by_date(self, reference_date):
        return self.db.load_history_by_date(reference_date)

    def list_room_types(self):
        return self.db.list_room_types()

    def list_rooms_with_type(self):
        return self.db.load_rooms_with_type()

    def list_consumptions(self):
        return self.db.list_consumptions()

    def create_room(self, room_number, room_type_id):
        existing = self.db.get_room_by_number(room_number)
        if existing:
            raise ValueError("Número de quarto já cadastrado.")

        self.db.insert_room(room_number, room_type_id)
        self.rooms.append(room_number)
        self.rooms.sort()
        self.refresh_room_types()

    def update_room_type_for_room(self, room_id, room_type_id):
        self.db.update_room_type_for_room(room_id, room_type_id)
        self.refresh_room_types()

    def save_consumption(self, consumption_id, name, price):
        existing = self.db.get_consumption_by_name(name)
        if existing and existing["id"] != consumption_id:
            raise ValueError("Insumo já cadastrado.")

        if consumption_id is None:
            self.db.insert_consumption(name, price)

        else:
            self.db.update_consumption(consumption_id, name, price)

        self.refresh_consumptions()

    def delete_consumption(self, consumption_id):
        self.db.delete_consumption(consumption_id)
        self.refresh_consumptions()

    def delete_room(self, room_id, room_number):
        if room_number in self.occupied:
            raise ValueError("Quarto ocupado. Faça checkout antes de excluir.")

        self.db.delete_room(room_id)
        if room_number in self.rooms:
            self.rooms.remove(room_number)

        self.refresh_room_types()

    def save_room_type(self, room_type_id, name, description, daily_rate):
        if room_type_id is None:
            return self.db.insert_room_type(name, description, daily_rate)

        self.db.update_room_type(room_type_id, name, description, daily_rate)
        return room_type_id

    def refresh_room_types(self):
        self.rooms_info = {
            item["room_number"]: {
                "room_type_id": item["room_type_id"],
                "room_type_name": item["room_type_name"],
                "daily_rate": float(item["daily_rate"]),
            }
            for item in self.db.load_rooms_with_type()
        }

    def refresh_consumptions(self):
        self.consumptions = self._load_consumptions()

    def get_room_type(self, room_number):
        return self.rooms_info.get(room_number, {}).get("room_type_name", "-")
