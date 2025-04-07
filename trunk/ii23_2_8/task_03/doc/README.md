# Лабораторная работа 3

## Тема: "Создание высокоуровневого макета сайта"

## Цель работы

 Cайт представляет собой макет высокого уровня без функциональной части. Реализовать возможность демонстрации работы сайта, заполняя поля необходимой информацией и демонстрируя переходы между страницами сайта.

## Задача
Вариант 8

Сайт рецептов.


## Требования

Основные страницы:
1. Главная страница: Список рецептов с возможностью фильтрации по
ингредиентам, сложности приготовления.
2. Детальная страница рецепта: Полное описание приготовления, список
ингредиентов, фото готового блюда.
3. Добавление рецепта: Форма для ввода названия рецепта, ингредиентов,
этапов приготовления, загрузки изображения.
4. Личный кабинет: Список добавленных рецептов и редактирование
профиля. 

## Ход выполнения:
Проект имеет следующую структуру:

```
project
├── app.py
├── recipes.csv
├── static/
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── detail.html
│   ├── add_recipe.html
│   ├── profile.html
│   └── login.html
```

Где recipes.csv - БД, имеющая вид:
![](images/1.png)
где,
```
id - номер рецепта;
title - название блюда; 
ingredients - ингридиенты, используемые для приготовления блюда;
complexity - сложность рецепта (Лёгкая, Средняя, Высокая);
steps - шаги приготовления блюда;
image_path - путь до изображения с готовым блюдом;
author - автор рецепт (рецепты, помеченные автором base - базовые и сразу есть в системе).
```
БД пополняется в ходе добавления рецептов.

## Код программы

```
import csv
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask("student_recipes_with_love")
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['CSV_FILE'] = 'recipes.csv'

def read_recipes_from_csv():
    recipes = []
    if not os.path.exists(app.config['CSV_FILE']):
        return recipes
    with open(app.config['CSV_FILE'], 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipes.append(row)
    return recipes

def write_recipes_to_csv(recipes):
    fieldnames = ['id', 'title', 'ingredients', 'complexity', 'steps', 'image_path', 'author']
    with open(app.config['CSV_FILE'], 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(recipe)

@app.route('/')
def index():
    recipes = read_recipes_from_csv()

    # Собираем все ингредиенты и все сложности для выпадающих списков
    all_ingredients = set()
    all_complexities = set()
    for r in recipes:
        for ing in r['ingredients'].split(','):
            all_ingredients.add(ing.strip())
        all_complexities.add(r['complexity'].strip())

    # Фильтрация
    ingredient_filter = request.args.get('ingredient', '').lower().strip()
    complexity_filter = request.args.get('complexity', '').lower().strip()

    filtered_recipes = []
    for r in recipes:
        ings_lower = [i.strip().lower() for i in r['ingredients'].split(',')]
        if ingredient_filter and ingredient_filter not in ings_lower:
            continue
        if complexity_filter and complexity_filter not in r['complexity'].lower():
            continue
        filtered_recipes.append(r)

    return render_template(
        'index.html',
        recipes=filtered_recipes,
        all_ingredients=sorted(all_ingredients),
        all_complexities=sorted(all_complexities)
    )

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipes = read_recipes_from_csv()
    recipe = None
    for r in recipes:
        if int(r['id']) == recipe_id:
            recipe = r
            break
    if not recipe:
        flash("Рецепт не найден!", "error")
        return redirect(url_for('index'))
    return render_template('detail.html', recipe=recipe)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if 'username' not in session:
        flash("Сначала авторизуйтесь!", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        complexity = request.form.get('complexity', '').strip()
        steps = request.form.get('steps', '').strip()
        author = session['username']

        image_file = request.files.get('image_file')
        image_path = ""
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(save_path)
            image_path = os.path.join('static/images', filename)

        recipes = read_recipes_from_csv()
        new_id = 1 if not recipes else max(int(r['id']) for r in recipes) + 1
        new_recipe = {
            'id': str(new_id),
            'title': title,
            'ingredients': ingredients,
            'complexity': complexity,
            'steps': steps,
            'image_path': image_path,
            'author': author
        }
        recipes.append(new_recipe)
        write_recipes_to_csv(recipes)

        flash("Рецепт успешно добавлен!", "success")
        return redirect(url_for('index'))

    return render_template('add_recipe.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash("Сначала авторизуйтесь!", "error")
        return redirect(url_for('login'))

    user = session['username']
    recipes = read_recipes_from_csv()
    my_recipes = [r for r in recipes if r['author'] == user]

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        if new_username:
            # Обновляем имя пользователя в сессии
            session['username'] = new_username
            flash("Имя пользователя успешно обновлено!", "success")
        else:
            flash("Имя пользователя не может быть пустым.", "error")

    return render_template('profile.html', user=user, recipes=my_recipes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            flash("Вы вошли в систему!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Введите имя пользователя!", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Вы вышли из системы!", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

```
 
## Результаты работы
1. Главная страница: Список рецептов с возможностью фильтрации по
ингредиентам, сложности приготовления.
![](images/2.png)
![](images/3.png)

 а) Возможность фильтрации по ингредиентам:

Список ингредиентов подтягивается из ingredients в recipes.csv и выводятся в алфавитном порядке.
![](images/4.png)

В качестве примера работы выберем игредиент: яйца
![](images/6.png)

 б) Возможность фильтрации по сложности приготовления:
![](images/5.png)
![](images/7.png)

 в) Применю оба фильтра: по сложности и по ингредиентам:
![](images/8.png)

 г) Кнопка "Все рецепты" выводит все рецепты:
![](images/9.png)


2. Детальная страница рецепта: Полное описание приготовления, список
ингредиентов, фото готового блюда.
![](images/10.png)
![](images/11.png)


3. Добавление рецепта: Форма для ввода названия рецепта, ингредиентов,
этапов приготовления, загрузки изображения.

Но перед тем как добавить рецепт необходимо авторизироваться:
![](images/13.png)
Если мы не вошли в аккаунт, то после нажатия на кнопку "Добавить рецепт", мы перейдём на следующую страницу:
![](images/12.png)
![](images/14.png)
Нажмём на "Добавить рецепт":
![](images/15.png)
Добавим рецепт медовика:
![](images/16.png)
Теперь в БД есть наш медовик:
![](images/17.png)
И на сайте появился новый рецкпт нашего Медовика:
![](images/18.png)
![](images/19.png)
![](images/20.png)

4. Личный кабинет: Список добавленных рецептов и редактирование
профиля.
Добавленный рецепт отобразился в нашем профиле.

![](images/22.png)
Редактирование профиля:
![](images/21.png)
Обновление имени пользователя:
![](images/23.png)