from flask import Flask, render_template, request, redirect, url_for, session, flash
import random



# Пример книг
books = [
    {'id': 1, 'title': '1984', 'author': 'George Orwell', 'rating': 4.8, 'image':'https://m.media-amazon.com/images/I/61NAx5pd6XL._AC_UF894,1000_QL80_.jpg', 'description': '1984 is a dystopian social science fiction novel and cautionary tale, written by the English writer George Orwell.'},
    {'id': 2, 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'rating': 4.7, 'image':'https://m.media-amazon.com/images/I/71FxgtFKcQL._AC_UF894,1000_QL80_.jpg', 'description': 'To Kill a Mockingbird is a 1960 Southern Gothic novel by American author Harper Lee. It became instantly successful after its release; in the United States, it is widely read in high schools and middle schools. To Kill a Mockingbird won the Pulitzer Prize a year after its release, and it has become a classic of modern American literature. The plot and characters are loosely based on Lees observations of her family, her neighbors and an event that occurred near her hometown of Monroeville, Alabama, in 1936, when she was ten.Despite dealing with the serious issues of rape and racial inequality, the novel is renowned for its warmth and humor. Atticus Finch, the narrators father, has served as a moral hero for many readers and as a model of integrity for lawyers. '},
    {'id': 3, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'rating': 4.5, 'image':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKi5lknrw7SIwZ01RQRqyvtXz2bFxrUsGVpA&s', 'description': 'The Great Gatsby is a 1925 novel by American writer F. Scott Fitzgerald that critiques the American Dream.'},
    {'id': 4, 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'rating': 4.6, 'image':'https://m.media-amazon.com/images/I/81Scutrtj4L._UF1000,1000_QL80_.jpg', 'description': 'Pride and Prejudice is a romantic novel by Jane Austen, first published in 1813.'},
    {'id': 5, 'title': 'Brave New World', 'author': 'Aldous Huxley', 'rating': 4.4, 'image':'https://m.media-amazon.com/images/I/71GNqqXuN3L._AC_UF894,1000_QL80_.jpg', 'description': 'Brave New World is a dystopian novel by Aldous Huxley, set in a future society of excessive control and state-imposed happiness.'},
    {'id': 6, 'title': 'Moby-Dick', 'author': 'Herman Melville', 'rating': 4.1, 'image':'https://m.media-amazon.com/images/I/71K4OH9CqOL._UF1000,1000_QL80_.jpg', 'description': 'Moby-Dick is a novel by Herman Melville about the obsession of Captain Ahab with capturing the great white whale.'},
    {'id': 7, 'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'rating': 4.2, 'image':'https://m.media-amazon.com/images/I/91fQEUwFMyL.jpg', 'description': 'The Catcher in the Rye is a 1951 novel by J.D. Salinger, dealing with complex themes of teenage rebellion and isolation.'},
    {'id': 8, 'title': 'Fahrenheit 451', 'author': 'Ray Bradbury', 'rating': 4.3, 'image':'https://upload.wikimedia.org/wikipedia/en/d/db/Fahrenheit_451_1st_ed_cover.jpg', 'description': 'Fahrenheit 451 is a dystopian novel by Ray Bradbury about a society where books are banned and burned.'},
    {'id': 9, 'title': 'Crime and Punishment', 'author': 'Fyodor Dostoevsky', 'rating': 4.9, 'image':'https://upload.wikimedia.org/wikipedia/en/4/4b/Crimeandpunishmentcover.png', 'description': 'Crime and Punishment is a novel by Fyodor Dostoevsky that explores the psychological torment of a young man after he commits murder.'},
    {'id': 10, 'title': 'The Hobbit', 'author': 'J.R.R. Tolkien', 'rating': 4.8, 'image':'https://m.media-amazon.com/images/I/81uEDUfKBZL.jpg', 'description': 'The Hobbit is a 1937 fantasy novel by J.R.R. Tolkien, which follows the journey of Bilbo Baggins.'}
]



@app.route('/')
def home():
    return render_template('home.html', books=books)

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return "Книга не найдена", 404

    # Получение отзывов
    reviews = session.get('reviews', [])
    book_reviews = [r['text'] for r in reviews if r['book_id'] == book_id]

    # Обработка формы отзыва
    if request.method == 'POST':
        review_text = request.form.get('review')
        if review_text:
            reviews.append({'book_id': book_id, 'text': review_text})
            session['reviews'] = reviews
            flash('Отзыв добавлен!')
        return redirect(url_for('book', book_id=book_id))

    is_favorite = book_id in session.get('favorites', [])
    return render_template('book.html', book=book, is_favorite=is_favorite, reviews=book_reviews)

@app.route('/add_to_favorites/<int:book_id>')
def add_to_favorites(book_id):
    favorites = session.get('favorites', [])
    if book_id not in favorites:
        favorites.append(book_id)
        session['favorites'] = favorites
        flash('Книга добавлена в избранное!')
    return redirect(url_for('book', book_id=book_id))

@app.route('/recommendations')
def recommendations():
    favorites_ids = session.get('favorites', [])

    # Фильтруем книги: исключаем те, что уже в избранном
    non_favorite_books = [book for book in books if book['id'] not in favorites_ids]


    return render_template('recommendations.html', books=non_favorite_books)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Получаем избранные книги
    favorites_ids = session.get('favorites', [])
    favorite_books = [b for b in books if b['id'] in favorites_ids]

    # Получаем текущие данные профиля
    profile_data = session.get('profile', {
        'nickname': '',
        'age': '',
        'country': ''
    })

    # Если форма отправлена — обновляем профиль
    if request.method == 'POST':
        profile_data['nickname'] = request.form.get('nickname', '')
        profile_data['age'] = request.form.get('age', '')
        profile_data['country'] = request.form.get('country', '')
        session['profile'] = profile_data
        flash("Профиль обновлён!")

    return render_template('profile.html', favorite_books=favorite_books, profile=profile_data)

if __name__ == '__main__':
    app.run(debug=True)
