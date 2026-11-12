from flask import Flask, request, session, redirect, url_for, render_template

app = Flask(__name__)
app.secret_key = 'super_secret_university_lab_key'

# Имитация базы данных пользователей
USERS = {
    1: {
        "username": "student",
        "password": "123",
        "full_name": "Иван Иванов (Студент)",
        "secret_note": "Мой пароль от Wi-Fi в общежитии: 987654321"
    },
    2: {
        "username": "admin",
        "password": "hard_password_999",
        "full_name": "Петр Петров (Преподаватель)",
        "secret_note": "Ответы на экзаменационные билеты лежат в сейфе."
    }
}

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        for uid, data in USERS.items():
            if data['username'] == username and data['password'] == password:
                session['user_id'] = uid
                # УЯЗВИМОСТЬ IDOR: ID пользователя передается открыто в URL
                return redirect(url_for('profile', user_id=uid))
        error = "Неверный логин или пароль"
        
    return render_template('login.html', error=error)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Проверка аутентификации
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # УЯЗВИМОСТЬ IDOR: берем ID из GET-параметра без сверки с session['user_id']
    requested_id = request.args.get('user_id', type=int)
    user = USERS.get(requested_id)
    
    if not user:
        return "Пользователь не найден", 404

    if request.method == 'POST':
        user['secret_note'] = request.form.get('new_note')

    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
