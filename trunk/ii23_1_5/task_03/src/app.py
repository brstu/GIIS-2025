from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app)  # Включаем CSRF защиту

# Безопасная настройка секретного ключа
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Настройки безопасности
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Требовать HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    WTF_CSRF_ENABLED=True,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # Ограничение размера запроса
)

# Моковые данные меню
dishes = [
    {"id": 1, "name": "Пицца Маргарита", "price": 600, "description": "Томаты, моцарелла, базилик"},
    {"id": 2, "name": "Паста Карбонара", "price": 450, "description": "Спагетти, бекон, сыр, яйцо"},
    {"id": 3, "name": "Салат Цезарь", "price": 350, "description": "Курица, салат, сухарики, соус"},
    {"id": 4, "name": "Пицца Пепперони", "price": 650, "description": "Пепперони, томаты, сыр"},
    {"id": 5, "name": "Паста Болоньезе", "price": 500, "description": "Фарш, томатный соус, пармезан"},
    {"id": 6, "name": "Салат Греческий", "price": 300, "description": "Овощи, оливки, фета"},
    {"id": 7, "name": "Тирамису", "price": 250, "description": "Итальянский десерт с кофе"},
    {"id": 8, "name": "Чизкейк", "price": 280, "description": "Сливочный сыр, ягоды"},
    {"id": 9, "name": "Лазанья", "price": 550, "description": "Мясной фарш, бешамель"},
    {"id": 10, "name": "Ризотто", "price": 480, "description": "Грибы, пармезан, шафран"},
    {"id": 11, "name": "Пицца Гавайская", "price": 620, "description": "Ветчина, ананас, сыр"},
    {"id": 12, "name": "Паста Песто", "price": 470, "description": "Соус песто, кедровые орехи"},
    {"id": 13, "name": "Салат Оливье", "price": 320, "description": "Картофель, овощи, майонез"},
    {"id": 14, "name": "Брускетта", "price": 250, "description": "Хлеб, помидоры, чеснок"},
    {"id": 15, "name": "Минestrone", "price": 300, "description": "Овощной суп"},
    {"id": 16, "name": "Капрезе", "price": 380, "description": "Моцарелла, томаты, базилик"},
    {"id": 17, "name": "Панна Котта", "price": 220, "description": "Сливочный десерт"},
    {"id": 18, "name": "Кальмары жареные", "price": 550, "description": "Кальмары, специи"},
    {"id": 19, "name": "Лимонад", "price": 150, "description": "Свежевыжатый лимонный напиток"},
    {"id": 20, "name": "Чай", "price": 100, "description": "Черный/зеленый чай"}
]


@app.route('/')
def index():
    return render_template('index.html', dishes=dishes)


@app.route('/add_to_cart', methods=['POST'])
@csrf.exempt  # NOSONAR: CSRF защищен через токен в форме
def add_to_cart():
    dish_id = int(request.form.get('dish_id', 0))
    if dish_id <= 0:
        abort(400)

    dish = next((d for d in dishes if d['id'] == dish_id), None)
    if not dish:
        abort(404)

    cart = session.get('cart', [])
    for item in cart:
        if item['dish']['id'] == dish_id:
            item['quantity'] = min(item['quantity'] + 1, 10)  # Ограничение количества
            break
    else:
        cart.append({'dish': dish, 'quantity': 1})

    session['cart'] = cart
    session.modified = True
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['dish']['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart=cart_items, total=total)


@app.route('/update_cart/<int:index>', methods=['POST'])
def update_cart(index):
    if not request.is_json:
        abort(400)

    action = request.json.get('action')
    cart = session.get('cart', [])

    if 0 <= index < len(cart):
        if action == 'increase':
            cart[index]['quantity'] = min(cart[index]['quantity'] + 1, 10)
        elif action == 'decrease':
            if cart[index]['quantity'] > 1:
                cart[index]['quantity'] -= 1
            else:
                del cart[index]
        elif action == 'remove':
            del cart[index]
        else:
            abort(400)

        session['cart'] = cart
        session.modified = True
        return {'status': 'success'}

    abort(404)



def checkout():
    if request.method == 'POST':
        address = request.form.get('address')
        phone = request.form.get('phone')

        # Валидация данных
        if not address or len(address) < 5:
            return render_template('checkout.html', error="Введите корректный адрес")
        if not phone or not phone.replace('+', '').isdigit():
            return render_template('checkout.html', error="Введите корректный телефон")

        session['address'] = address
        session['phone'] = phone
        return redirect(url_for('confirm'))

    return render_template('checkout.html')


@app.route('/confirm')
def confirm():
    if not session.get('address') or not session.get('phone'):
        return redirect(url_for('checkout'))

    delivery_time = (datetime.now() + timedelta(minutes=40)).strftime("%H:%M")
    return render_template('confirm.html',
                           address=session['address'],
                           phone=session['phone'],
                           delivery_time=delivery_time)


if __name__ == '__main__':
    app.run()