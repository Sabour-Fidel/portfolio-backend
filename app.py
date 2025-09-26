from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# Autorise seulement ton domaine GitHub Pages en production
CORS(app, resources={r"/*": {"origins": "*"}})  # Temporairement * pour tests

# Initialiser la DB
def init_db():
    conn = sqlite3.connect('stats.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY, views INTEGER DEFAULT 0, shares INTEGER DEFAULT 0)''')
    cursor.execute('INSERT OR IGNORE INTO stats (id) VALUES (1)')
    conn.commit()
    conn.close()

init_db()

# Récupérer les stats
def get_stats():
    conn = sqlite3.connect('stats.db')
    cursor = conn.cursor()
    cursor.execute('SELECT views, shares FROM stats WHERE id=1')
    row = cursor.fetchone()
    conn.close()
    return {'views': row[0], 'shares': row[1]}

# Incrémenter un champ
def increment(field):
    conn = sqlite3.connect('stats.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE stats SET {field} = {field} + 1 WHERE id=1')
    conn.commit()
    conn.close()
    return get_stats()

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(get_stats())

@app.route('/view', methods=['POST'])
def view():
    return jsonify(increment('views'))

@app.route('/share', methods=['POST'])
def share():
    return jsonify(increment('shares'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)