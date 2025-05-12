from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
secret = os.environ.get('SECRET_KEY')
if not secret:
    raise RuntimeError("SECRET_KEY must be set in environment for production.")
app.config['SECRET_KEY'] = secret
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
app.config['WTF_CSRF_SSL_STRICT'] = True

csrf = CSRFProtect(app)

# 🔹 Примерные данные о поездах
trains = [
    {
        'id': 1,
        'number': '101А',
        'from_city': 'Москва',
        'to_city': 'Санкт-Петербург',
        'departure_time': '08:00',
        'arrival_time': '12:00',
        'available_seats': ['1A', '1B', '2A', '2B']
    },
    {
        'id': 2,
        'number': '202Б',
        'from_city': 'Казань',
        'to_city': 'Москва',
        'departure_time': '14:30',
        'arrival_time': '22:00',
        'available_seats': ['3A', '3B', '4A']
    },
]

# 🔹 Хранилище билетов
# 🔹 Начальные билеты для тестирования
tickets = [
    {
        'id': 1,
        'train_id': 1,
        'train_number': '101А',
        'from_city': 'Москва',
        'to_city': 'Санкт-Петербург',
        'seat': '1A',
        'passenger_name': 'Иван Иванов',
        'passenger_email': 'ivan@example.com'
    },
    {
        'id': 2,
        'train_id': 2,
        'train_number': '202Б',
        'from_city': 'Казань',
        'to_city': 'Москва',
        'seat': '3B',
        'passenger_name': 'Мария Смирнова',
        'passenger_email': 'maria@example.com'
    }
]

# Удаление занятых мест из поездов
for ticket in tickets:
    train = next((t for t in trains if t['id'] == ticket['train_id']), None)
    if train and ticket['seat'] in train['available_seats']:
        train['available_seats'].remove(ticket['seat'])


# Главная — поиск маршрутов
@app.route('/')
def home():
    return render_template('home.html')

# Результаты поиска
@app.route('/search')
def search_results():
    from_city = request.args.get('from_city', '').strip().lower()
    to_city = request.args.get('to_city', '').strip().lower()
    date = request.args.get('date')

    filtered_trains = [
        t for t in trains
        if from_city in t['from_city'].lower() and to_city in t['to_city'].lower()
    ]
    return render_template('search_results.html', trains=filtered_trains)

# Выбор места и оформление билета
# Показ формы бронирования (GET)
@app.route('/book/<int:train_id>', methods=['GET'])
def show_booking_form(train_id):
    train = next((t for t in trains if t['id'] == train_id), None)
    if not train:
        flash('Поезд не найден', 'error')
        return redirect(url_for('home'))
    return render_template('book_ticket.html', train=train)

# Обработка бронирования (POST)
@app.route('/book/<int:train_id>', methods=['POST'])
def process_booking(train_id):
    train = next((t for t in trains if t['id'] == train_id), None)
    if not train:
        flash('Поезд не найден', 'error')
        return redirect(url_for('home'))

    passenger_name = request.form.get('passenger_name')
    passenger_email = request.form.get('passenger_email')
    seat = request.form.get('seat')

    if not passenger_name or not passenger_email or not seat:
        flash('Пожалуйста, заполните все поля', 'error')
        return redirect(url_for('show_booking_form', train_id=train_id))

    if seat not in train['available_seats']:
        flash('Выбранное место недоступно', 'error')
        return redirect(url_for('show_booking_form', train_id=train_id))

    # Удаление места из доступных
    train['available_seats'].remove(seat)

    ticket = {
        'id': len(tickets) + 1,
        'train_id': train['id'],
        'train_number': train['number'],
        'from_city': train['from_city'],
        'to_city': train['to_city'],
        'seat': seat,
        'passenger_name': passenger_name,
        'passenger_email': passenger_email
    }
    tickets.append(ticket)
    return redirect(url_for('confirmation', ticket_id=ticket['id']))


# Подтверждение покупки
@app.route('/confirmation/<int:ticket_id>')
def confirmation(ticket_id):
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        flash('Билет не найден', 'error')
        return redirect(url_for('home'))
    return render_template('confirmation.html', ticket=ticket)

# Личный кабинет
@app.route('/profile')
def profile():
    return render_template('profile.html', tickets=tickets)

# Отмена билета
@app.route('/cancel/<int:ticket_id>')
def cancel_ticket(ticket_id):
    global tickets
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        flash('Билет не найден', 'error')
        return redirect(url_for('profile'))

    # Вернуть место обратно
    train = next((t for t in trains if t['id'] == ticket['train_id']), None)
    if train:
        train['available_seats'].append(ticket['seat'])

    tickets = [t for t in tickets if t['id'] != ticket_id]
    flash('Билет отменен', 'success')
    return redirect(url_for('profile'))

# Запуск
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
