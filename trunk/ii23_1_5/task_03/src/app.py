from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
def add_to_cart():
    dish_id = int(request.form.get('dish_id'))
    dish = next(d for d in dishes if d['id'] == dish_id)

    cart = session.get('cart', [])
    for item in cart:
        if item['dish']['id'] == dish_id:
            item['quantity'] += 1
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


@app.route('/increase_quantity/<int:index>')
def increase_quantity(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart[index]['quantity'] += 1
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart'))


@app.route('/decrease_quantity/<int:index>')
def decrease_quantity(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        if cart[index]['quantity'] > 1:
            cart[index]['quantity'] -= 1
        else:
            del cart[index]
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart'))


@app.route('/remove_item/<int:index>')
def remove_item(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        del cart[index]
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        session['address'] = request.form['address']
        session['phone'] = request.form['phone']
        return redirect(url_for('confirm'))
    return render_template('checkout.html')


@app.route('/confirm')
def confirm():
    delivery_time = (datetime.now() + timedelta(minutes=40)).strftime("%H:%M")
    return render_template('confirm.html',
                           address=session.get('address'),
                           phone=session.get('phone'),
                           delivery_time=delivery_time)


if __name__ == '__main__':
    app.run()