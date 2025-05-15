import sqlite3
from hashlib import sha256
import os


class DataBaseConnector:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'database.db')

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_all_tables()

    def create_all_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS threats (
         ID INTEGER,
         Type TEXT (100),
         Created_at datetime,
         Description TEXT (100),
         Indicator TEXT (100),
         is_active BOOL
         );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                 Username TEXT (100),
                 Password TEXT (100)
                 );""")
        self.connection.commit()

    def _insert_if_not_exists(self, item: dict) -> None:
        """Вспомогательная функция для вставки записи, если indicator не существует."""
        self.cursor.execute('SELECT 1 FROM threats WHERE Indicator = ?', (item["indicator"],))
        exists = self.cursor.fetchone()

        if not exists:
            self.cursor.execute('''
                INSERT INTO threats (ID, Type, Created_at, Description, Indicator, is_active) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                                (
                                    item["id"],  # ID
                                    item["type"],  # Type
                                    item["created"],  # Created_at
                                    item["description"],  # Description
                                    item["indicator"],  # Indicator
                                    item["is_active"]  # is_active
                                ))
            self.connection.commit()

    def import_to_database(self, json_data: dict) -> None:
        """Импорт из JSON файла."""
        for item in json_data["item"]:
            self._insert_if_not_exists(item)

        print("Данные успешно импортированы в БД!")

    def insert_threat(self, threat_data: dict) -> None:
        """Добавление одного фида через API или вручную."""
        self._insert_if_not_exists(threat_data)
        print("Фид успешно добавлен!")

    def search_threats(self, search_text='', filter_type='') -> list:
        query = "SELECT ID, Type, Created_at, Description, Indicator, is_active FROM threats WHERE 1=1"
        params = []

        if search_text:
            query += " AND Indicator LIKE ?"
            params.append(f"%{search_text}%")

        if filter_type:
            query += " AND Type = ?"
            params.append(filter_type)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def create_new_user(self, user_data: dict) -> bool:
        self.cursor.execute('SELECT 1 FROM users WHERE Username = ?', (user_data["username"],))
        exists = self.cursor.fetchone()

        if not exists:
            self.cursor.execute('''
                            INSERT INTO users (Username, Password) 
                            VALUES (?, ?)''',
                                (
                                    user_data["username"],
                                    user_data["password"]
                                ))
            self.connection.commit()
            return True
        else:
            return False

    def user_authorization(self, user_data: dict) -> bool:
        self.cursor.execute('SELECT Password FROM users WHERE Username = ?', (user_data["username"],))
        exists = self.cursor.fetchone()

        if exists:
            db_password = exists[0]
            password = sha256(user_data["password"].encode('utf-8')).hexdigest()

            return db_password == password

        return False

    def drop_table(self):
        self.cursor.execute("""DROP TABLE threats""")
        self.connection.commit()
