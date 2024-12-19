from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos desde variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

# Configuración de carga de archivos
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicialización de la base de datos
db = SQLAlchemy(app)

# MODELO: Pacientes
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folio_expediente = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    sexo = db.Column(db.String(10))
    tratamiento = db.Column(db.String(255))
    indice_higiene = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    foto_frente = db.Column(db.String(255))
    foto_intraoral = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

# MODELO: Asistencia
class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), nullable=False)
    nombre_estudiante = db.Column(db.String(100), nullable=False)
    folio_paciente = db.Column(db.String(50), nullable=False)
    grupo = db.Column(db.String(50))
    fecha = db.Column(db.String(20))
    hora = db.Column(db.String(10))

# RUTA: Página principal
@app.route("/")
def index():
    return "¡Hola desde Flask conectado a Supabase!"

# RUTA: Gestión de Pacientes
@app.route("/pacientes", methods=["GET", "POST"])
def pacientes():
    if request.method == "POST":
        folio_expediente = request.form.get("folio_expediente")
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        sexo = request.form.get("sexo")
        tratamiento = request.form.get("tratamiento")
        indice_higiene = request.form.get("indice_higiene")
        observaciones = request.form.get("observaciones")

        # Procesar imágenes
        foto_frente = request.files.get("foto_frente")
        filename_frente = None
        if foto_frente and '.' in foto_frente.filename:
            filename_frente = os.path.join(app.config['UPLOAD_FOLDER'], foto_frente.filename)
            foto_frente.save(filename_frente)

        nuevo_paciente = Paciente(
            folio_expediente=folio_expediente,
            nombre=nombre,
            edad=edad,
            sexo=sexo,
            tratamiento=tratamiento,
            indice_higiene=indice_higiene,
            observaciones=observaciones,
            foto_frente=filename_frente
        )
        db.session.add(nuevo_paciente)
        db.session.commit()
        flash("Paciente agregado correctamente.", "success")
        return redirect(url_for("pacientes"))

    pacientes = Paciente.query.all()
    return render_template("pacientes.html", pacientes=pacientes)

# Inicializar la base de datos
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
