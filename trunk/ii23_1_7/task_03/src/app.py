from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import os
import secrets

app = Flask(__name__, static_folder='static')

# Конфигурация безопасности
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Генерация безопасного ключа
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Время жизни CSRF-токена (1 час)

# Включение CSRF-защиты
csrf = CSRFProtect(app)

# Mock данные об отелях
hotels = [
    {
        'id': 1,
        'name': 'Роскошный Отель',
        'location': 'Москва',
        'price': 5000,
        'rating': 4.8,
        'image': 'moscow.jpg',
        'description': 'Прекрасный отель в самом центре Москвы с видом на Красную площадь.',
        'rooms': [
            {'type': 'Стандарт', 'price': 5000, 'available': 10},
            {'type': 'Люкс', 'price': 10000, 'available': 5},
            {'type': 'Президентский', 'price': 25000, 'available': 2}
        ],
        'amenities': ['Бесплатный Wi-Fi', 'Бассейн', 'Спа', 'Ресторан'],
        'reviews': [
            {'author': 'Иван', 'rating': 5, 'text': 'Отличный отель, прекрасный сервис!'},
            {'author': 'Мария', 'rating': 4, 'text': 'Хороший отель, но дорогой.'}
        ]
    },
    {
        'id': 2,
        'name': 'Пляжный Курорт',
        'location': 'Сочи',
        'price': 7500,
        'rating': 4.5,
        'image': 'sochi.jpg',
        'description': 'Курортный отель с собственным пляжем и прекрасным видом на море.',
        'rooms': [
            {'type': 'Стандарт', 'price': 7500, 'available': 15},
            {'type': 'Семейный', 'price': 12000, 'available': 7},
            {'type': 'Бунгало', 'price': 18000, 'available': 3}
        ],
        'amenities': ['Бесплатный Wi-Fi', 'Пляж', 'Ресторан', 'Детский клуб'],
        'reviews': [
            {'author': 'Алексей', 'rating': 5, 'text': 'Прекрасное место для отдыха с семьей!'},
            {'author': 'Ольга', 'rating': 4, 'text': 'Хороший сервис, но далеко от центра.'}
        ]
    },
    {
        'id': 3,
        'name': 'Горный Клуб',
        'location': 'Альпы',
        'price': 9000,
        'rating': 4.9,
        'image': 'alps.jpg',
        'description': 'Эксклюзивный горный курорт с видом на Альпы и спа-комплексом.',
        'rooms': [
            {'type': 'Стандарт', 'price': 9000, 'available': 8},
            {'type': 'Сьют', 'price': 15000, 'available': 4},
            {'type': 'Шале', 'price': 22000, 'available': 3}
        ],
        'amenities': ['Бесплатный Wi-Fi', 'Спа', 'Ресторан', 'Горные лыжи'],
        'reviews': [
            {'author': 'Дмитрий', 'rating': 5, 'text': 'Незабываемые виды и сервис!'},
            {'author': 'Елена', 'rating': 5, 'text': 'Идеальное место для активного отдыха.'}
        ]
    }
]

bookings = []

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    if search_query:
        filtered_hotels = [h for h in hotels if search_query.lower() in h['location'].lower() or
                           search_query.lower() in h['name'].lower()]
    else:
        filtered_hotels = hotels
    return render_template('home.html', hotels=filtered_hotels, search_query=search_query)

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = next((h for h in hotels if h['id'] == hotel_id), None)
    if not hotel:
        return redirect(url_for('home'))
    return render_template('hotel_detail.html', hotel=hotel)

@app.route('/book/<int:hotel_id>', methods=['GET', 'POST'])
def book_hotel(hotel_id):
    hotel = next((h for h in hotels if h['id'] == hotel_id), None)
    if not hotel:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Валидация данных формы
        guest_name = request.form.get('guest_name', '').strip()
        guest_email = request.form.get('guest_email', '').strip()
        room_type = request.form.get('room_type', '').strip()
        check_in = request.form.get('check_in', '').strip()
        nights = request.form.get('nights', '').strip()

        if not all([guest_name, guest_email, room_type, check_in, nights]):
            return render_template('booking_form.html', hotel=hotel, error="Все поля обязательны для заполнения.")

        try:
            nights = int(nights)
            if nights <= 0:
                raise ValueError
        except ValueError:
            return render_template('booking_form.html', hotel=hotel, error="Неверное количество ночей.")

        # Проверка доступности номера
        room = next((r for r in hotel['rooms'] if r['type'] == room_type), None)
        if not room or room['available'] <= 0:
            return render_template('booking_form.html', hotel=hotel, error="Выбранный номер недоступен.")

        # Обработка бронирования
        booking_data = {
            'hotel_id': hotel_id,
            'hotel_name': hotel['name'],
            'guest_name': guest_name,
            'guest_email': guest_email,
            'room_type': room_type,
            'check_in': check_in,
            'nights': nights,
            'total_price': room['price'] * nights,
            'booking_id': len(bookings) + 1
        }

        bookings.append(booking_data)
        return redirect(url_for('booking_confirmation', booking_id=booking_data['booking_id']))

    return render_template('booking_form.html', hotel=hotel)

@app.route('/booking/<int:booking_id>')
def booking_confirmation(booking_id):
    if booking_id <= 0 or booking_id > len(bookings):
        return redirect(url_for('home'))

    booking = bookings[booking_id - 1]
    hotel = next((h for h in hotels if h['id'] == booking['hotel_id']), None)

    return render_template('booking_confirmation.html', booking=booking, hotel=hotel)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 0 < booking_id <= len(bookings):
        bookings.pop(booking_id - 1)
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=False)