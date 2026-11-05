import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


# Инициализация тестовой БД в оперативной памяти
def init_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            secret_note TEXT
        )
    """
    )
    sample_data = [
        ("admin", "admin@corp.local", "Супер-секретный пароль: Admin123!"),
        ("ivan", "ivan@mail.ru", "Купить молоко и хлеб."),
        (
            "elena",
            "elena@company.com",
            "Секретный ключ проекта: XYZ-999-ABC",
        ),
    ]
    cursor.executemany(
        "INSERT INTO users (username, email, secret_note) VALUES (?, ?, ?)",
        sample_data,
    )
    conn.commit()
    return conn


db_conn = init_db()


@app.route("/")
def index():
    # Рендерим файл templates/index.html
    return render_template("index.html")


@app.route("/search")
def search():
    user_input = request.args.get("username", "")

    # УЯЗВИМОСТЬ: Прямая склейка строки запроса с вводом пользователя
    query = (
        f"SELECT username, email FROM users WHERE username = '{user_input}'"
    )

    cursor = db_conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
    except Exception as e:
        rows = []
        query = f"{query} | Ошибка SQL: {str(e)}"

    # Передаем данные в шаблон templates/search.html
    return render_template("search.html", rows=rows, executed_query=query)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
