from flask import Blueprint, request, render_template, redirect, session, url_for, flash
from database_module.database_module import DataBaseConnector
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename


user_blueprint = Blueprint('user', __name__)
db_connector = DataBaseConnector()


# Директория для загрузки файлов
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for('user.index'))

    if request.method == "POST":
        data = {
            'username': request.form["username"],
            'password': request.form["password"]
        }

        is_authorization = db_connector.user_authorization(data)

        if is_authorization:
            session['user'] = request.form["username"]
            return redirect(url_for('user.index'))
        else:
            error = "Неверный логин или пароль"
            return render_template("login.html", error=error)
    return render_template("login.html")


@user_blueprint.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for('user.login'))

    search_text = request.form.get('search', '')
    filter_type = request.form.get('filter', '')

    results = db_connector.search_threats(search_text, filter_type)
    types = ['FileHash-MD5', 'FileHash-SHA1', 'FileHash-SHA256', 'IPv4', 'hostname', 'CVE', 'URL', 'domain']

    return render_template('index.html', results=results, types=types, search_text=search_text, filter_type=filter_type)


@user_blueprint.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('user.login'))


@user_blueprint.route("/upload_feed", methods=["GET"])
def upload_feed():
    if "user" not in session:
        return redirect(url_for('user.login'))
    return render_template("upload_feed.html")


@user_blueprint.route("/upload_single_feed", methods=["POST"])
def upload_single_feed():
    if "user" not in session:
        return redirect(url_for('user.login'))

    # Генерация ID автоматически
    generated_id = str(uuid.uuid4().int)[:6]

    # Текущее время создания
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Собираем данные в словарь
    new_feed = {
        "id": generated_id,
        "type": request.form["type"],
        "created": created_at,
        "description": request.form["description"],
        "indicator": request.form["indicator"],
        "is_active": True if request.form.get("active") == "true" else False
    }

    # Добавляем в базу
    db_connector.insert_threat(new_feed)

    flash('Фид успешно добавлен!', 'success')
    return redirect(url_for('user.upload_feed'))


@user_blueprint.route("/upload_json_feed", methods=["POST"])
def upload_json_feed():
    if "user" not in session:
        return redirect(url_for('user.login'))

    file = request.files.get("file")
    if not file:
        flash('Ошибка: Файл не выбран.', 'danger')
        return redirect(url_for('user.upload_feed'))

    # Проверяем, что файл имеет расширение .json
    if not file.filename.endswith('.json'):
        flash('Ошибка: Можно загружать только JSON файлы.', 'danger')
        return redirect(url_for('user.upload_feed'))

    # Сохраняем файл
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Проверяем наличие ключа "item" и его правильный тип
        if "item" not in data or not isinstance(data["item"], list):
            flash('Ошибка: Неверный формат JSON файла.', 'danger')
            return redirect(url_for('user.upload_feed'))

        # Вызываем функцию импорта
        db_connector.import_to_database(data)

        flash('Фиды успешно загружены из файла!', 'success')
        return redirect(url_for('user.upload_feed'))

    except json.JSONDecodeError:
        flash('Ошибка: Файл не является валидным JSON.', 'danger')
        return redirect(url_for('user.upload_feed'))
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'danger')
        return redirect(url_for('user.upload_feed'))
