import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Page, expect  

BASE_URL = "http://127.0.0.1:5000"

def test_sql_injection_delete_all():
    """
    ДИНАМИЧЕСКИЙ ТЕСТ НА SQL-ИНЪЕКЦИЮ (SQLi)
    Проверяем, уязвима ли функция удаления к вектору '1 OR 1=1'
    """
    # Отправляем вредоносный SQL-запрос в параметре id
    attack_url = f"{BASE_URL}/delete?id=1+OR+1=1"
    requests.get(attack_url)

    # Проверяем результат: если уязвимость есть, база очистится полностью
    response = requests.get(f"{BASE_URL}/")

    # Ожидаем отсутствие элемента с классом для заметок
    soup = BeautifulSoup(response.text, 'html.parser')
    notes = soup.find_all(class_="note")
    
    # Если уязвимость сработала, список notes должен быть абсолютно пустым (длина 0)
    assert len(notes) == 0, "Заметки не удалены"


def test_stored_xss_vulnerability(page: Page):
    """
    ДИНАМИЧЕСКИЙ ТЕСТ НА XSS С ПРОВЕРКОЙ ВЫПОЛНЕНИЯ ALERT
    Использует реальный браузер Chromium под капотом.
    """
    # Флаг, который переключится в True, если браузер поймает всплывающее окно alert
    alert_triggered = False
    alert_message = ""

    # Настраиваем перехватчик событий типа "dialog" (alert, prompt, confirm)
    def handle_dialog(dialog):
        nonlocal alert_triggered, alert_message
        alert_triggered = True
        alert_message = dialog.message
        dialog.accept()  # Закрываем окно, чтобы тест не завис

    page.on("dialog", handle_dialog)

    # Отправляем вредоносную заметку через обычный POST-запрос (для скорости)
    # Код пытается вызвать alert('XSS_SUCCESS')
    payload = {"title": "Хакерская заметка", "content": "<script>alert('XSS_SUCCESS')</script>"}
    requests.post(f"{BASE_URL}/add", data=payload)

    # Открываем страницу в реальном браузере Playwright
    page.goto(BASE_URL)

    # Браузер загружает HTML, видит тег <script> (благодаря уязвимости | safe) и выполняет его
    # В этот момент срабатывает наш обработчик handle_dialog

    # Проверяем, что alert действительно был запущен и содержит правильный текст
    assert alert_triggered, "Уязвимость НЕ сработала: браузер не запустил функцию alert()."
    assert alert_message == "XSS_SUCCESS", f"Alert сработал, но текст некорректен: {alert_message}"
