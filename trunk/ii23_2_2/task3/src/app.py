from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app) 

app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    WTF_CSRF_ENABLED=True,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'menu.json'), 'r', encoding='utf-8') as f:
    MENU = json.load(f)


def find_dish(dish_id):
    return next((dish for dish in MENU if dish.get("id") == dish_id), None)


def get_cart():
    return session.setdefault('cart', [])


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


@app.route('/')
def home():
    return render_template('index.html', dishes=MENU)


@app.route('/order', methods=['POST'])
@csrf.exempt 
def order_item():
    dish_id = int(request.form.get('dish_id', -1))
    dish = find_dish(dish_id)
    if not dish:
        abort(404)

    cart = get_cart()
    for item in cart:
        if item['dish']['id'] == dish_id:
            item['quantity'] = min(item['quantity'] + 1, 10)
            break
    else:
        cart.append({'dish': dish, 'quantity': 1})

    save_cart(cart)
    return redirect(url_for('home'))


@app.route('/basket')
def basket_view():
    cart = get_cart()
    total = sum(entry['dish']['price'] * entry['quantity'] for entry in cart)
    return render_template('cart.html', cart=cart, total=total)


@app.route('/change/<int:item_index>', methods=['POST'])
def change_item(item_index):
    if not request.is_json:
        abort(400)

    cart = get_cart()
    action = request.json.get('action')

    if not (0 <= item_index < len(cart)):
        abort(404)

    if action == 'increase':
        cart[item_index]['quantity'] = min(cart[item_index]['quantity'] + 1, 10)
    elif action == 'decrease':
        if cart[item_index]['quantity'] > 1:
            cart[item_index]['quantity'] -= 1
        else:
            cart.pop(item_index)
    elif action == 'remove':
        cart.pop(item_index)
    else:
        abort(400)

    save_cart(cart)
    return {'status': 'ok'}


@app.route('/checkout', methods=['GET', 'POST'])
def do_checkout():
    if request.method == 'POST':
        addr = request.form.get('address')
        phone = request.form.get('phone')

        if not addr or len(addr) < 5:
            return render_template('checkout.html', error="Некорректный адрес")
        if not phone or not phone.replace('+', '').isdigit():
            return render_template('checkout.html', error="Некорректный телефон")

        session['order_info'] = {'address': addr, 'phone': phone}
        return redirect(url_for('confirmation'))

    return render_template('checkout.html')


@app.route('/confirmation')
def confirmation():
    info = session.get('order_info')
    if not info:
        return redirect(url_for('do_checkout'))

    expected_time = (datetime.now() + timedelta(minutes=40)).strftime('%H:%M')
    return render_template('confirm.html', address=info['address'],
                           phone=info['phone'], delivery_time=expected_time)


if __name__ == '__main__':
    app.run(debug=True)
