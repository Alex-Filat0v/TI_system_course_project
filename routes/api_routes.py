from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from database_module.database_module import DataBaseConnector
from datetime import datetime
import uuid
import os
import json

api_blueprint = Blueprint('api', __name__)
db_connector = DataBaseConnector()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@api_blueprint.route("/upload_single_feed", methods=["POST"])
@jwt_required()
def api_upload_single_feed():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Нет данных в запросе."}), 400

    feed_type = data.get("type")
    description = data.get("description")
    indicator = data.get("indicator")
    active = data.get("active", True)

    if not all([feed_type, description, indicator]):
        return jsonify({"error": "Поля 'type', 'description' и 'indicator' обязательны."}), 400

    # Генерируем ID и дату создания
    generated_id = str(uuid.uuid4().int)[:6]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Собираем фид
    new_feed = {
        "id": generated_id,
        "type": feed_type,
        "created": created_at,
        "description": description,
        "indicator": indicator,
        "is_active": bool(active)
    }

    try:
        db_connector.insert_threat(new_feed)
        return jsonify({"message": "Фид успешно добавлен.", "feed": new_feed}), 201
    except Exception as e:
        return jsonify({"error": f"Ошибка добавления фида: {str(e)}"}), 500


@api_blueprint.route("/upload_json_file", methods=["POST"])
@jwt_required()
def api_upload_json_file():
    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден в запросе."}), 400

    file = request.files["file"]
    if not file.filename.endswith('.json'):
        return jsonify({"error": "Неверный формат файла. Требуется .json."}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "item" not in data or not isinstance(data["item"], list):
            return jsonify({"error": "Неверный формат JSON файла. Ожидался ключ 'item' со списком."}), 400

        db_connector.import_to_database(data)

        return jsonify({"message": "Фиды успешно загружены из JSON файла."}), 201
    except json.JSONDecodeError:
        return jsonify({"error": "Файл не является валидным JSON."}), 400
    except Exception as e:
        return jsonify({"error": f"Ошибка обработки файла: {str(e)}"}), 500



@api_blueprint.route("/get_feeds", methods=["POST"])
def get_feeds():
    data = request.get_json()
    search_text = data.get("search_text", "")
    filter_type = data.get("filter_type", "")
    print(filter_type)
    results = db_connector.search_threats(search_text, filter_type)

    return jsonify(results), 201
