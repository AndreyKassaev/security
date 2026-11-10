from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# Секретный ключ для подписи сессионных cookie
app.secret_key = 'super_secret_demo_key'

# Имитация базы данных пользователей (слабые пароли для демонстрации)
USERS = {
    'admin': '123456',
    'user': 'qwerty',
    'test': 'password'
}

@app.route('/')
def index():
    # Если пользователь уже авторизован, перенаправляем в аккаунт
    if 'username' in session:
        return redirect(url_for('account'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # УЯЗВИМОСТЬ: Нет задержки при проверке, нет счетчика неудачных попыток,
        # нет капчи и нет блокировки по IP или логину.
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('account'))
        else:
            # Явное сообщение об ошибке облегчает автоматизированный анализ ответа
            error = 'Неверный логин или пароль'

    return render_template('login.html', error=error)

@app.route('/account')
def account():
    # Проверка наличия активной сессии
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('account.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Запуск сервера в режиме отладки на локальном хосте
    app.run(host='127.0.0.1', port=5000, debug=True)
