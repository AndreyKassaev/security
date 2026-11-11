import os
import time
import random
import secrets
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

USERS = {
    'admin': generate_password_hash('123456'),
    'user': generate_password_hash('qwerty'),
    'test': generate_password_hash('password')
}

# Настройки защиты
CAPTCHA_THRESHOLD = 2     # После скольких ошибок показывать капчу
MAX_ATTEMPTS = 5          # После скольких ошибок блокировать полностью
LOCKOUT_TIME = 300        # Время блокировки в секундах (5 минут)

FAILED_ATTEMPTS = {}

def generate_captcha():
    """Генерирует простую математическую задачу и сохраняет ответ в сессии."""
    a = random.randint(1, 15)
    b = random.randint(1, 15)
    session['captcha_answer'] = str(a + b)
    return f"Сколько будет {a} + {b}?"

def get_attempts_count(identifier):
    """Возвращает текущее число неудачных попыток."""
    record = FAILED_ATTEMPTS.get(identifier)
    return record['count'] if record else 0

def is_locked(identifier):
    """Проверяет, заблокирован ли IP или логин."""
    record = FAILED_ATTEMPTS.get(identifier)
    if not record:
        return False, 0
    
    if record['lock_until'] > time.time():
        remaining = int(record['lock_until'] - time.time())
        return True, remaining
    
    if record['lock_until'] != 0:
        FAILED_ATTEMPTS.pop(identifier, None)
    return False, 0

def register_failure(identifier):
    """Увеличивает счетчик неудач и при достижении лимита активирует блокировку."""
    record = FAILED_ATTEMPTS.setdefault(identifier, {'count': 0, 'lock_until': 0})
    record['count'] += 1
    
    if record['count'] >= MAX_ATTEMPTS:
        record['lock_until'] = time.time() + LOCKOUT_TIME

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('account'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    client_ip = request.remote_addr
    username = request.form.get('username', '').strip() if request.method == 'POST' else ''

    # Проверяем, нужно ли требовать капчу для данного IP или логина
    attempts = max(
        get_attempts_count(f"ip:{client_ip}"),
        get_attempts_count(f"user:{username}") if username else 0
    )
    require_captcha = attempts >= CAPTCHA_THRESHOLD

    if request.method == 'POST':
        password = request.form.get('password', '')
        user_captcha = request.form.get('captcha', '').strip()

        # 1. Проверка полной блокировки
        ip_locked, ip_wait = is_locked(f"ip:{client_ip}")
        user_locked, user_wait = is_locked(f"user:{username}")

        if ip_locked or user_locked:
            wait_time = max(ip_wait, user_wait)
            error = f'Слишком много попыток входа. Повторите через {wait_time} сек.'
            return render_template('login.html', error=error), 429

        # 2. Проверка капчи, если порог ошибок уже превышен
        if require_captcha:
            expected_answer = session.pop('captcha_answer', None)
            if not expected_answer or user_captcha != expected_answer:
                register_failure(f"ip:{client_ip}")
                error = 'Неверный ответ на проверочный вопрос'
                captcha_question = generate_captcha()
                return render_template('login.html', error=error, captcha_question=captcha_question), 400

        # 3. Искусственная задержка
        time.sleep(1.5)

        # 4. Проверка логина и пароля
        user_hash = USERS.get(username)
        dummy_hash = 'scrypt:32768:8:1$dummy$00000000000000000000000000000000'
        
        if user_hash and check_password_hash(user_hash, password):
            # Успешный вход: сбрасываем счетчики и очищаем капчу
            FAILED_ATTEMPTS.pop(f"ip:{client_ip}", None)
            FAILED_ATTEMPTS.pop(f"user:{username}", None)
            session.pop('captcha_answer', None)
            
            session['username'] = username
            return redirect(url_for('account'))
        else:
            if not user_hash:
                check_password_hash(dummy_hash, password)
                
            register_failure(f"ip:{client_ip}")
            if username:
                register_failure(f"user:{username}")
                
            error = 'Неверный логин или пароль'
            
            # Пересчитываем, не пора ли показать капчу после текущей ошибки
            new_attempts = max(
                get_attempts_count(f"ip:{client_ip}"),
                get_attempts_count(f"user:{username}") if username else 0
            )
            captcha_question = generate_captcha() if new_attempts >= CAPTCHA_THRESHOLD else None
            return render_template('login.html', error=error, captcha_question=captcha_question), 401

    # Для GET-запроса: если лимит ошибок уже достигнут ранее, сразу показываем капчу
    captcha_question = generate_captcha() if require_captcha else None
    return render_template('login.html', error=error, captcha_question=captcha_question)

@app.route('/account')
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('account.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
