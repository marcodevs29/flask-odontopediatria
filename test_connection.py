from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:brunorakan0729%40@db.rvrjnixqeffqbhgrvalj.supabase.co:5432/postgres?sslmode=require"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_size': 5,
    'connect_args': {
        'connect_timeout': 30
    }
}

db = SQLAlchemy(app)

@app.route('/')
def test_connection():
    try:
        result = db.session.execute(text('SELECT 1'))
        db.session.commit()
        return 'Conexión exitosa a la base de datos!'
    except Exception as e:
        return f'Error de conexión: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)