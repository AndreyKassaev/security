import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)


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
    return render_template("index.html")


@app.route("/search")
def search():
    user_input = request.args.get("username", "")

    # ЗАЩИТА 1: Используем плейсхолдер (?) вместо форматирования строки
    query = "SELECT username, email FROM users WHERE username = ?"

    cursor = db_conn.cursor()

    try:
        # ЗАЩИТА 2: Передаем пользовательский ввод отдельным кортежем
        cursor.execute(query, (user_input,))
        rows = cursor.fetchall()
        debug_info = f"Запрос: {query} | Параметр: '{user_input}'"
    except Exception:
        # ЗАЩИТА 3: Не выводим сырой текст ошибки БД пользователю
        rows = []
        debug_info = "Произошла внутренняя ошибка при обработке запроса."

    return render_template("search.html", rows=rows, executed_query=debug_info)


if __name__ == "__main__":
    app.run(debug=False, port=5000)
