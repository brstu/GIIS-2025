from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

CACHE_CONTROL_HEADER = 'no-store, max-age=0'

# Фиксированные данные поездов
trains = [
    {
        "id": 1,
        "name": "Сапсан",
        "departure_time": "08:00",
        "arrival_time": "12:30",
        "price": 25,
        "seats": {
            "Плацкарт": [{"number": i, "occupied": random.choice([True, False])} for i in range(1, 31)],
            "Купе": [{"number": i, "occupied": random.choice([True, False])} for i in range(31, 41)],
            "Люкс": [{"number": i, "occupied": random.choice([True, False])} for i in range(41, 51)]
        }
    }
]

tickets = []


def calculate_trip_duration(departure_time, arrival_time):
    dep = datetime.strptime(departure_time, "%H:%M")
    arr = datetime.strptime(arrival_time, "%H:%M")
    if arr < dep: arr += timedelta(days=1)
    duration = arr - dep
    return f"{duration.seconds // 3600} ч {(duration.seconds % 3600) // 60} мин"


@app.route('/')
def index():
    session.clear()
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = CACHE_CONTROL_HEADER
    return response


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        session['from'] = request.form.get('from')
        session['to'] = request.form.get('to')
        session['date'] = request.form.get('date')
        return redirect(url_for('search_results'))

    return redirect(url_for('index'))


@app.route('/search_results')
def search_results():
    if not all(key in session for key in ['from', 'to', 'date']):
        return redirect(url_for('index'))

    results = []
    for train in trains:
        results.append({
            **train,
            "departure": f"{session['date']} {train['departure_time']}",
            "arrival": f"{session['date']} {train['arrival_time']}"
        })

    response = make_response(render_template(
        'search_results.html',
        trains=results,
        from_city=session['from'],
        to_city=session['to'],
        travel_date=session['date'],
        calculate_trip_duration=calculate_trip_duration
    ))
    response.headers['Cache-Control'] = CACHE_CONTROL_HEADER
    return response


@app.route('/train/<int:train_id>')
def train_details(train_id):
    if not all(key in session for key in ['from', 'to', 'date']):
        return redirect(url_for('index'))

    train = next((t for t in trains if t['id'] == train_id), None)
    if not train:
        return redirect(url_for('search_results'))

    train_with_dates = {
        **train,
        "departure": f"{session['date']} {train['departure_time']}",
        "arrival": f"{session['date']} {train['arrival_time']}"
    }

    response = make_response(render_template(
        'confirmation.html',
        train=train_with_dates,
        from_city=session['from'],
        to_city=session['to'],
        travel_date=session['date'],
        calculate_trip_duration=calculate_trip_duration,
        seats=train['seats']  # Добавляем информацию о местах
    ))
    response.headers['Cache-Control'] = CACHE_CONTROL_HEADER
    return response


@app.route('/book', methods=['POST'])
def book():
    try:
        train_id = int(request.form.get('train_id'))
        passenger_name = request.form.get('passenger_name')
        passenger_email = request.form.get('passenger_email')
        carriage_type = request.form.get('carriage_type')
        seat_number = request.form.get('seat_number')

        train = next((t for t in trains if t['id'] == train_id), None)
        if not train:
            flash('Поезд не найден', 'danger')
            return redirect(url_for('index'))

        # Помечаем место как занятое
        for seat in train['seats'][carriage_type]:
            if str(seat['number']) == seat_number:
                seat['occupied'] = True
                break

        # Создаем билет
        ticket = {
            'id': len(tickets) + 1,
            'train_id': train_id,
            'train_name': train['name'],
            'from': session['from'],
            'to': session['to'],
            'date': session['date'],
            'departure': f"{session['date']} {train['departure_time']}",
            'arrival': f"{session['date']} {train['arrival_time']}",
            'price': train['price'],
            'passenger_name': passenger_name,
            'passenger_email': passenger_email,
            'carriage_type': carriage_type,
            'seat_number': seat_number,
            'booking_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'Подтвержден'
        }
        tickets.append(ticket)

        flash('Билет успешно забронирован!', 'success')
        return redirect(url_for('profile'))
    except Exception as e:
        flash(f'Ошибка бронирования: {str(e)}', 'danger')
        return redirect(url_for('index'))


@app.route('/cancel/<int:ticket_id>')
def cancel(ticket_id):
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if ticket:
        ticket['status'] = 'Отменен'
        flash('Бронирование отменено', 'success')
    else:
        flash('Билет не найден', 'danger')
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    response = make_response(render_template('profile.html', tickets=tickets))
    response.headers['Cache-Control'] = CACHE_CONTROL_HEADER
    return response


if __name__ == '__main__':
    app.run(debug=True)