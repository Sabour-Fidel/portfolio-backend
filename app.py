from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
# Autorise uniquement ton domaine GitHub Pages
CORS(app, resources={r"/*": {"origins": "https://sabour-fidel.github.io"}})

# URL de connexion PostgreSQL (utilise une variable d'environnement)
DATABASE_URL = os.environ.get('DATABASE_URL')

# Fonction pour se connecter à la DB
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Initialiser la DB
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS stats (
            id SERIAL PRIMARY KEY,
            views INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0
        )''')
        # Insère une ligne par défaut si elle n'existe pas
        cursor.execute('INSERT INTO stats (views, shares) VALUES (0, 0) ON CONFLICT DO NOTHING')
        conn.commit()
    except psycopg2.Error as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
    finally:
        cursor.close()
        conn.close()

# Appelle init_db au démarrage de l'app
with app.app_context():
    init_db()

# Récupérer les stats
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT views, shares FROM stats LIMIT 1')
        row = cursor.fetchone()
        if row is None:
            init_db()  # Réinitialise si la table est vide
            return {'views': 0, 'shares': 0}
        return {'views': row[0], 'shares': row[1]}
    except psycopg2.Error as e:
        print(f"Erreur lors de la récupération des stats : {e}")
        return {'views': 0, 'shares': 0}
    finally:
        cursor.close()
        conn.close()

# Incrémenter un champ
def increment(field):
    if field not in ['views', 'shares']:
        raise ValueError(f"Champ invalide : {field}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE stats SET {field} = {field} + 1')
        conn.commit()
        return get_stats()
    except psycopg2.Error as e:
        print(f"Erreur lors de l'incrémentation de {field} : {e}")
        raise
    finally:
        cursor.close()
        conn.close()

@app.route('/stats', methods=['GET'])
def stats():
    try:
        return jsonify(get_stats())
    except Exception as e:
        return jsonify({'error': f'Erreur serveur : {str(e)}'}), 500

@app.route('/view', methods=['POST'])
def view():
    try:
        return jsonify(increment('views'))
    except Exception as e:
        return jsonify({'error': f'Erreur serveur : {str(e)}'}), 500

@app.route('/share', methods=['POST'])
def share():
    try:
        return jsonify(increment('shares'))
    except Exception as e:
        return jsonify({'error': f'Erreur serveur : {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)