from hashlib import sha256


from database_module.database_module import DataBaseConnector


db_connector = DataBaseConnector()


def create_new_user() -> None:
    username = str(input("Введите имя нового пользователя: "))
    password = str(input("Введите пароль нового пользователя: "))

    password = sha256(password.encode('utf-8')).hexdigest()

    data = {
        'username': username,
        'password': password
    }

    answer = db_connector.create_new_user(data)

    if answer:
        print("Пользователь успешно добавлен в базу данных")
    else:
        print("Такой пользователь уже существует")
        create_new_user()


if __name__ == '__main__':
    create_new_user()
