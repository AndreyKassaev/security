import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = "notes.db" 

def init_db():
    # Каждый запуск с чистого листа
    if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except PermissionError:
                # Если Flask держит файл, очищаем таблицы вручную
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS notes")
                conn.commit()
                conn.close()

    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    # Создаем простую таблицу для заметок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
    ''')
    # Добавляем демо-данные, если база пуста
    cursor.execute("SELECT COUNT(*) FROM notes")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO notes (title, content) VALUES ('Секрет', 'Мой пароль от почты: SuperSecret123')")
        cursor.execute("INSERT INTO notes (title, content) VALUES ('Покупки', 'Купить молоко, хлеб и сыр.')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM notes")
    notes = cursor.fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form.get('title')
    content = request.form.get('content')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    # Безопасная запись для демонстрации разницы (здесь используются плейсхолдеры)
    cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ЗАВЕДОМО УЯЗВИМЫЙ МАРШРУТ (SQL-инъекция)
@app.route('/delete')
def delete_note():
    note_id = request.args.get('id')
    
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    # Уязвимость: конкатенация строк вместо параметризации (?,)
    # Злоумышленник может манипулировать логикой запроса
    query = f"DELETE FROM notes WHERE id = {note_id}"
    
    try:
        cursor.executescript(query) # executescript позволяет выполнять цепочки команд через ';'
        conn.commit()
    except Exception as e:
        print(f"Ошибка выполнения SQL: {e}")
    finally:
        conn.close()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
