from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)

RECAPTCHA_SECRET_KEY = "6LfOx9gqAAAAAAUCzr2SC14VTXbwUYRpEIh5re0r"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/contact', methods=['POST'])
def contact():
    data = request.json
    recaptcha_token = data.get('recaptchaToken')

    # Verify reCAPTCHA with Google
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    response = requests.post(recaptcha_url, data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": recaptcha_token
    })

    result = response.json()

    if not result.get("success"):
        return jsonify({"message": "reCAPTCHA verification failed"}), 400

    # Store message in SQLite
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
