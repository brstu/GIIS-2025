from flask import Flask, render_template, request, redirect, url_for, session, flash

#app = Flask(__name__)
#я убрал ключ т.к. ругалось при проверке что секретный ключ разглашать нельзя

dishes = [
    {
        "id": 1,
        "name": "Пицца Маргарита",
        "price": 450,
        "description": "Классическая пицца с томатным соусом, моцареллой и базиликом",
        "image": "pizza-margherita.jpg"
    },
    {
        "id": 2,
        "name": "Паста Карбонара",
        "price": 380,
        "description": "Спагетти с соусом из яиц, пармезана, гуанчиале и перца",
        "image": "pasta-carbonara.jpg"
    },
    {
        "id": 3,
        "name": "Салат Цезарь",
        "price": 320,
        "description": "Салат с курицей, листьями айсберга, крутонами и соусом цезарь",
        "image": "caesar-salad.jpg"
    }
]


@app.route('/')
def index():
    return render_template('index.html', dishes=dishes)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        dish_id = int(request.form.get('dish_id'))
        dish = next((d for d in dishes if d['id'] == dish_id), None)

        if not dish:
            flash('Блюдо не найдено', 'error')
            return redirect(url_for('index'))

        if 'cart' not in session:
            session['cart'] = []

        session['cart'].append(dish)
        session.modified = True
        flash(f'{dish["name"]} добавлен в корзину!', 'success')
    except Exception as e:
        flash('Ошибка при добавлении в корзину', 'error')
        app.logger.error(f'Error adding to cart: {str(e)}')

    return redirect(url_for('index'))


@app.route('/cart')
def view_cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] for item in cart_items) if cart_items else 0
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if 'cart' in session and 0 <= index < len(session['cart']):
        removed_item = session['cart'].pop(index)
        session.modified = True
        flash(f'{removed_item["name"]} удален из корзины', 'info')
    return redirect(url_for('view_cart'))


@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('view_cart'))
    return render_template('checkout.html')


@app.route('/confirm_order', methods=['POST'])  # Изменили с 'confirm' на 'confirm_order'
def confirm_order():
    try:
        if 'cart' not in session or not session['cart']:
            flash('Ваша корзина пуста', 'warning')
            return redirect(url_for('view_cart'))

        order_details = {
            'name': request.form.get('name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'comments': request.form.get('comments'),
            'items': session['cart'],
            'total': sum(item['price'] for item in session['cart'])
        }

        session['order_details'] = order_details
        session.pop('cart', None)

        return redirect(url_for('order_confirmation'))
    except Exception as e:
        flash('Ошибка при оформлении заказа', 'error')
        app.logger.error(f'Order confirmation error: {str(e)}')
        return redirect(url_for('checkout'))


@app.route('/order_confirmation')
def order_confirmation():
    if 'order_details' not in session:
        flash('Нет данных о заказе', 'error')
        return redirect(url_for('index'))
    return render_template('confirmation.html', order_details=session['order_details'])


if __name__ == '__main__':
    app.run(debug=True)