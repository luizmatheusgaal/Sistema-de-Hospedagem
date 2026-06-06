from datetime import datetime
import os

import pymysql

from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self._ensure_database()
        self.connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT")),
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _ensure_database(self):
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT")),
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        connection.close()

    def create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tipo_quarto (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(60) NOT NULL,
                    descricao VARCHAR(200) NOT NULL,
                    valor_diaria DECIMAL(10, 2) NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quartos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    numero INT NOT NULL UNIQUE,
                    tipo_id INT NOT NULL,
                    FOREIGN KEY (tipo_id) REFERENCES tipo_quarto(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS ocupacoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    quarto_id INT NOT NULL,
                    nome VARCHAR(120) NOT NULL,
                    dias INT NOT NULL,
                    checkin DATETIME NOT NULL,
                    consumo DECIMAL(10, 2) NOT NULL,
                    reserva VARCHAR(20) NOT NULL,
                    ativo TINYINT(1) NOT NULL DEFAULT 1,
                    FOREIGN KEY (quarto_id) REFERENCES quartos(id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS estadias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    quarto_id INT NOT NULL,
                    nome VARCHAR(120) NOT NULL,
                    dias INT NOT NULL,
                    checkin DATETIME NOT NULL,
                    checkout DATETIME NOT NULL,
                    consumo DECIMAL(10, 2) NOT NULL,
                    total DECIMAL(10, 2) NOT NULL,
                    reserva VARCHAR(20) NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS faturamento_diario (
                    data DATE PRIMARY KEY,
                    total DECIMAL(10, 2) NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS consumos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(80) NOT NULL UNIQUE,
                    valor DECIMAL(10, 2) NOT NULL
                )
                """
            )

    def _get_room_id(self, room_number):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id FROM quartos WHERE numero = %s", (room_number,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Quarto não encontrado.")
            return result["id"]

    def load_occupancies(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT q.numero AS room_number, o.nome AS guest_name, o.dias AS days,
                       o.checkin, o.consumo AS consumption, o.reserva AS reservation
                FROM ocupacoes o
                JOIN quartos q ON q.id = o.quarto_id
                WHERE o.ativo = 1
                """
            )
            return cursor.fetchall()

    def insert_room(self, room_number, room_type_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO quartos (numero, tipo_id)
                VALUES (%s, %s)
                """,
                (room_number, room_type_id),
            )
            return cursor.lastrowid

    def get_room_by_number(self, room_number):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, numero, tipo_id
                FROM quartos
                WHERE numero = %s
                """,
                (room_number,),
            )
            return cursor.fetchone()

    def update_room_type_for_room(self, room_id, room_type_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE quartos
                SET tipo_id = %s
                WHERE id = %s
                """,
                (room_type_id, room_id),
            )

    def delete_room(self, room_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM quartos
                WHERE id = %s
                """,
                (room_id,),
            )

    def list_consumptions(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome AS name, valor AS price
                FROM consumos
                ORDER BY nome
                """
            )
            return cursor.fetchall()

    def get_consumption_by_name(self, name):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome AS name, valor AS price
                FROM consumos
                WHERE nome = %s
                """,
                (name,),
            )
            return cursor.fetchone()

    def insert_consumption(self, name, price):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO consumos (nome, valor)
                VALUES (%s, %s)
                """,
                (name, price),
            )
            return cursor.lastrowid

    def update_consumption(self, consumption_id, name, price):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE consumos
                SET nome = %s, valor = %s
                WHERE id = %s
                """,
                (name, price, consumption_id),
            )

    def delete_consumption(self, consumption_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM consumos
                WHERE id = %s
                """,
                (consumption_id,),
            )

    def load_history_by_date(self, reference_date):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT q.numero AS room_number, e.nome AS guest_name, e.dias AS days,
                       e.checkin, e.checkout, e.consumo AS consumption, e.total,
                       e.reserva AS reservation, t.nome AS room_type_name,
                       t.valor_diaria AS daily_rate
                FROM estadias e
                JOIN quartos q ON q.id = e.quarto_id
                JOIN tipo_quarto t ON t.id = q.tipo_id
                WHERE DATE(checkout) = %s
                ORDER BY checkout
                """,
                (reference_date,),
            )
            return cursor.fetchall()

    def load_history(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT q.numero AS room_number, e.nome AS guest_name, e.dias AS days,
                       e.checkin, e.checkout, e.consumo AS consumption, e.total,
                       e.reserva AS reservation, t.nome AS room_type_name,
                       t.valor_diaria AS daily_rate
                FROM estadias e
                JOIN quartos q ON q.id = e.quarto_id
                JOIN tipo_quarto t ON t.id = q.tipo_id
                ORDER BY checkout
                """
            )
            return cursor.fetchall()

    def load_rooms_with_type(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT q.id, q.numero AS room_number, t.id AS room_type_id,
                       t.nome AS room_type_name, t.valor_diaria AS daily_rate
                FROM quartos q
                JOIN tipo_quarto t ON t.id = q.tipo_id
                ORDER BY q.numero
                """
            )
            return cursor.fetchall()

    def list_room_types(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome AS name, descricao AS description, valor_diaria AS daily_rate
                FROM tipo_quarto
                ORDER BY id
                """
            )
            return cursor.fetchall()

    def insert_room_type(self, name, description, daily_rate):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tipo_quarto (nome, descricao, valor_diaria)
                VALUES (%s, %s, %s)
                """,
                (name, description, daily_rate),
            )
            return cursor.lastrowid

    def update_room_type(self, room_type_id, name, description, daily_rate):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tipo_quarto
                SET nome = %s, descricao = %s, valor_diaria = %s
                WHERE id = %s
                """,
                (name, description, daily_rate, room_type_id),
            )

    def insert_checkin(self, room_number, guest_name, stay_days, checkin_time, reservation):
        with self.connection.cursor() as cursor:
            room_id = self._get_room_id(room_number)
            cursor.execute(
                """
                INSERT INTO ocupacoes (quarto_id, nome, dias, checkin, consumo, reserva, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                """,
                (room_id, guest_name, stay_days, checkin_time, 0.0, reservation),
            )

    def add_consumption(self, room_number, amount):
        with self.connection.cursor() as cursor:
            room_id = self._get_room_id(room_number)
            cursor.execute(
                """
                UPDATE ocupacoes
                SET consumo = consumo + %s
                WHERE quarto_id = %s AND ativo = 1
                """,
                (amount, room_id),
            )

    def finalize_checkout(
        self,
        room_number,
        consumption,
        total,
        reservation,
        guest_name,
        stay_days,
        checkin_time,
    ):
        with self.connection.cursor() as cursor:
            room_id = self._get_room_id(room_number)
            cursor.execute(
                """
                INSERT INTO estadias (quarto_id, nome, dias, checkin, checkout, consumo, total, reserva)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    room_id,
                    guest_name,
                    stay_days,
                    checkin_time,
                    datetime.now(),
                    consumption,
                    total,
                    reservation,
                ),
            )
            cursor.execute(
                """
                UPDATE ocupacoes
                SET ativo = 0
                WHERE quarto_id = %s AND ativo = 1
                """,
                (room_id,),
            )

    def calculate_daily_revenue(self, reference_date):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(total, 0) AS total
                FROM faturamento_diario
                WHERE data = %s
                """,
                (reference_date,),
            )
            result = cursor.fetchone()
            return float(result["total"] if result else 0.0)

    def add_daily_revenue(self, reference_date, amount):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO faturamento_diario (data, total)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE total = total + VALUES(total)
                """,
                (reference_date, amount),
            )
