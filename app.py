from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuración de Supabase (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:brunorakan0729@rvrjnixqeffqbhgrvalj.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key'

# Inicialización de la base de datos
db = SQLAlchemy(app)

# Probar la conexión
@app.route('/test_db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return "Conexión exitosa a Supabase PostgreSQL"
    except Exception as e:
        return f"Error en la conexión: {str(e)}"
    
# Configuración de carga de archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

# RUTA: Eliminar Paciente
@app.route("/eliminar_paciente/<int:id>")
def eliminar_paciente(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)
    db.session.commit()
    flash("Paciente eliminado correctamente.", "danger")
    return redirect(url_for("pacientes"))

# RUTA: Control de Asistencia
@app.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    fecha_actual = datetime.now().strftime("%d/%m/%Y")  # Fecha actual
    if request.method == "POST":
        matricula = request.form.get("matricula")
        nombre_estudiante = request.form.get("nombre_estudiante")
        folio_paciente = request.form.get("folio_paciente")
        grupo = request.form.get("grupo")
        hora = request.form.get("hora")

        nueva_asistencia = Asistencia(
            matricula=matricula,
            nombre_estudiante=nombre_estudiante,
            folio_paciente=folio_paciente,
            grupo=grupo,
            fecha=fecha_actual,
            hora=hora
        )
        db.session.add(nueva_asistencia)
        db.session.commit()
        flash("Asistencia registrada correctamente.", "success")
        return redirect(url_for("asistencia"))

    asistencias = Asistencia.query.all()
    return render_template("asistencia.html", asistencias=asistencias, fecha_actual=fecha_actual)

# RUTA: Descargar base de datos
@app.route("/descargar")
def descargar():
    return send_file("gestion_clinica.db", as_attachment=True)

# Inicializar la base de datos
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
