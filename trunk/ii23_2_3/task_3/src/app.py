from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_wtf import CSRFProtect
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)


# Пример списка товаров
items = [
    {
        'name': 'Смартфон Samsung Galaxy S9',
        'category': 'Электроника',
        'condition': 'Хорошее',
        'price': 7000,
        'image': 'item1.png',
        'description': 'Отличное состояние, без трещин.',
    },
    {
        'name': 'Кресло IKEA',
        'category': 'Мебель',
        'condition': 'Как новое',
        'price': 4500,
        'image': 'item2.jpg',
        'description': 'Удобное кресло, почти не использовалось.',
    },
    {
        'name': 'Книга "1984" Дж. Оруэлл',
        'category': 'Книги',
        'condition': 'Б/у',
        'price': 300,
        'image': 'item3.jpg',
        'description': 'Пару страниц с загибами.',
    },
]

# Хранилище заявок
requests_list = []

@app.route('/')
def index():
    return render_template('all_items.html', items=items)

@app.route('/account')
def account():
    user = {'name': 'Пользователь'}
    return render_template('account.html', user=user)

@app.route('/requests')
def requests_view():
    return render_template('requests.html', requests=requests_list)

@app.route('/request_item', methods=['POST'])
def request_item():
    item_name = request.form.get('item_name')
    item_price = request.form.get('item_price')

    requests_list.append({
        'item': item_name,
        'price': item_price,
        'date': datetime.now().strftime('%d.%m.%Y'),
        'status': 'Ожидает ответа'
    })
    return redirect(url_for('request_success'))

@app.route('/request_success')
def request_success():
    return render_template('request_success.html')

if __name__ == '__main__':
    app.run(debug=False)
