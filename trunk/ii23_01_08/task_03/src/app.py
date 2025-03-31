from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

recipes = [
    {
        'id': 2,
        'title': 'Ляфуфунь аля шеф',
        'ingredients': ['Баклажан', 'соль'],
        'instructions': 'Баклажан',
        'difficulty': 'Легкая',
        'image': 'https://avatars.mds.yandex.net/get-entity_search/1880293/935922551/S600xU_2x',
        'author': 'Саня Компас'
    }
]

users = {
    'user1': {
        'name': 'Иван Иванов',
        'email': 'ivan@example.com',
        'recipes': [1]
    }
}


@app.route('/')
def home():

    difficulty_filter = request.args.get('difficulty')
    ingredient_filter = request.args.get('ingredient')

    filtered_recipes = recipes

    if difficulty_filter:
        filtered_recipes = [r for r in filtered_recipes if r['difficulty'] == difficulty_filter]

    if ingredient_filter:
        filtered_recipes = [r for r in filtered_recipes if
                            ingredient_filter.lower() in [i.lower() for i in r['ingredients']]]

    return render_template('home.html', recipes=filtered_recipes)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if not recipe:
        return redirect(url_for('home'))
    return render_template('recipe_detail.html', recipe=recipe)


@methods.route('/compliant1')
def add_recipe():
    if request.method == 'POST':

        new_recipe = {
            'id': len(recipes) + 1,
            'title': request.form.get('title'),
            'ingredients': [x.strip() for x in request.form.get('ingredients').split(',')],
            'instructions': request.form.get('instructions'),
            'difficulty': request.form.get('difficulty'),
            'image': request.form.get('image_url') or 'https://via.placeholder.com/400x300',
            'author': 'Текущий пользователь'
        }
        recipes.append(new_recipe)
        return redirect(url_for('recipe_detail', recipe_id=new_recipe['id']))

    return render_template('add_recipe.html')


@app.route('/profile')
def profile():

    user = users['user1']
    user_recipes = [r for r in recipes if r['id'] in user['recipes']]
    return render_template('profile.html', user=user, recipes=user_recipes)


@methods.route('/compliant1')
def edit_profile():
    user = users['user1']
    if request.method == 'POST':

        user['name'] = request.form.get('name')
        user['email'] = request.form.get('email')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)


if __name__ == '__main__':
    app.debug = False
    app.run(debug=False)
