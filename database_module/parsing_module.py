import os
from dotenv import load_dotenv
import requests
import json
from database_module.json_module import JsonConnector
from database_module.database_module import DataBaseConnector


load_dotenv()

API_URL = os.getenv('API_URL')
API_KEY = os.getenv('API_KEY')

db = DataBaseConnector()
jsonmanager = JsonConnector()


def collect_data(end):
    for i in range(1, end + 1):

        headers = {
            'X-OTX-API-KEY': API_KEY
        }

        response = requests.get(f"{API_URL}?page={i}", headers=headers)

        if response.status_code == 200:
            data = response.json()

            jsonmanager.import_to_json(data)

            with open('new.json', 'r') as file:
                json_data = json.load(file)
                db.import_to_database(json_data)
            os.remove('new.json')

        else:
            print("Ошибка при получении данных:", response.status_code)

        print(f"{i} готов")
