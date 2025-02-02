from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import random

app = Flask(__name__)

# Временное хранилище данных пользователя
users = []

# Функция для получения случайных туров
def get_random_tours(limit=4):
    conn = sqlite3.get_db_connection()
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users.append({'email': email, 'password': password})
        print(f"Новый пользователь: {email}")
        return redirect(url_for('tours'))
    return render_template('register.html', show_exit_button=True)

@app.route('/tours')
def tours():
    random_tours = get_random_tours()
    tour_data = []
    for name, folder_path in random_tours:
        image_path = os.path.join(folder_path, 'image.jpg')
        description = load_tour_description(folder_path)
        tour_data.append({
            'name': name,
            'image_path': image_path,
            'description': description
        })
    return render_template('tours.html', show_exit_button=True, tours=tour_data)

if __name__ == '__main__':
    app.run(debug=True)