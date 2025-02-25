import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Секретный ключ для работы с flash-сообщениями

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('travel_site/tours.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для получения случайных туров
def get_random_tours(limit=4):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, folder_path FROM tours')
    all_tours = cursor.fetchall()
    conn.close()
    return random.sample(all_tours, min(limit, len(all_tours)))

# Функция для загрузки описания тура
def load_tour_description(folder_path):
    description_path = os.path.join(folder_path, 'description.txt')
    if os.path.exists(description_path):
        with open(description_path, 'r', encoding='utf-8') as file:
            return file.read()
    return "Описание тура отсутствует."

@app.route('/')
def index():
    return render_template('index.html', show_exit_button=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Пользователь успешно вошёл
            return redirect(url_for('tours'))
        else:
            # Неверные данные
            flash('Неверная почта или пароль', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', show_exit_button=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))

        # Хэшируем пароль
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('tours'))  # Перенаправляем на страницу с турами
        except sqlite3.IntegrityError:
            flash('Пользователь с такой почтой уже существует', 'error')
        finally:
            conn.close()

    return render_template('register.html', show_exit_button=True)


@app.route('/tours')
def tours():
    random_tours = get_random_tours()
    tour_data = []
    for name, folder_path in random_tours:
        image_path = os.path.join(folder_path, 'image.jpg').replace('\\', '/')
        image_path = image_path.replace('travel_site/static/', '')
        description = load_tour_description(folder_path)
        tour_data.append({
            'name': name,
            'image_path': image_path,
            'description': description
        })
    return render_template('tours.html', show_exit_button=True, tours=tour_data)

if __name__ == '__main__':
    app.run(debug=False)
