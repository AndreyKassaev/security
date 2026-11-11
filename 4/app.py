from flask import Flask, request, redirect, url_for, session, render_template

app = Flask(__name__)
app.secret_key = 'super_secret_educational_key'

# Имитация базы данных
users_db = {
    'admin': {
        'password': 'password123',
        'bio': 'Администратор системы',
        'email': 'admin@example.com'
    },
    'user': {
        'password': '123',
        'bio': 'Обычный пользователь',
        'email': 'user@example.com'
    }
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('account'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users_db.get(username)
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('account'))
        else:
            error = 'Неверный логин или пароль'
            
    return render_template('login.html', error=error)

@app.route('/account')
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session['username']
    user_data = users_db.get(username)
    return render_template('account.html', username=username, user_data=user_data)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    username = session['username']
    new_email = request.form.get('email')
    new_bio = request.form.get('bio')
    
    if new_email:
        users_db[username]['email'] = new_email
    if new_bio is not None:
        users_db[username]['bio'] = new_bio
        
    return redirect(url_for('account'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Настройки для наглядной демонстрации уязвимостей
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = None
    app.run(debug=True, port=5000)
