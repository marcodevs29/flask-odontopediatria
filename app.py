from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configuración de carga de archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = 'datos_clinicos.db'

# Función de inicialización de la base de datos
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Tabla para la gestión de pacientes
        cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            folio_expediente TEXT UNIQUE,
                            nombre TEXT,
                            edad INTEGER,
                            sexo TEXT,
                            tratamiento TEXT,
                            indice_higiene TEXT,
                            organos_tratados TEXT,
                            tratamientos_realizados TEXT,
                            observaciones TEXT,
                            evaluacion TEXT,
                            recibo_pago TEXT,
                            estatus_pago TEXT,
                            foto_frente TEXT,
                            foto_intraoral TEXT,
                            foto_indice TEXT,
                            foto_procedimiento TEXT
                        )''')
        # Tabla para control de asistencia
        cursor.execute('''CREATE TABLE IF NOT EXISTS asistencia (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            matricula TEXT,
                            nombre_estudiante TEXT,
                            folio_paciente TEXT,
                            grupo TEXT,
                            fecha TEXT,
                            hora TEXT
                        )''')
        conn.commit()

# Ruta principal
@app.route('/')
def index():
    return redirect(url_for('pacientes'))

# Ruta para gestión de pacientes
@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if request.method == 'POST':
        # Recibir datos del formulario
        folio_expediente = request.form.get('folio_expediente')
        nombre = request.form.get('nombre')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        tratamiento = request.form.get('tratamiento')
        indice_higiene = request.form.get('indice_higiene')
        organos_tratados = request.form.get('organos_tratados')
        tratamientos_realizados = request.form.get('tratamientos_realizados')
        observaciones = request.form.get('observaciones')
        evaluacion = request.form.get('evaluacion')
        recibo_pago = request.form.get('recibo_pago')
        estatus_pago = request.form.get('estatus_pago')

        # Procesar imágenes
        imagenes = {}
        for campo in ['foto_frente', 'foto_intraoral', 'foto_indice', 'foto_procedimiento']:
            file = request.files.get(campo)
            if file and '.' in file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagenes[campo] = filename
            else:
                imagenes[campo] = None

        # Guardar datos en la base de datos
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO pacientes (folio_expediente, nombre, edad, sexo, tratamiento, 
                            indice_higiene, organos_tratados, tratamientos_realizados, observaciones, 
                            evaluacion, recibo_pago, estatus_pago, foto_frente, foto_intraoral, foto_indice, 
                            foto_procedimiento)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (folio_expediente, nombre, edad, sexo, tratamiento, indice_higiene, organos_tratados,
                            tratamientos_realizados, observaciones, evaluacion, recibo_pago, estatus_pago,
                            imagenes['foto_frente'], imagenes['foto_intraoral'], imagenes['foto_indice'],
                            imagenes['foto_procedimiento']))
            conn.commit()
            flash('Información del paciente guardada correctamente.', 'success')

        return redirect(url_for('pacientes'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes")
        pacientes = cursor.fetchall()
    return render_template('pacientes.html', pacientes=pacientes)

# Ruta para control de asistencia
@app.route('/asistencia', methods=['GET', 'POST'])
def asistencia():
    fecha_actual = datetime.now().strftime("%d/%m/%Y")  # Fecha en formato DD/MM/YYYY

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nombre_estudiante = request.form.get('nombre_estudiante')
        folio_paciente = request.form.get('folio_paciente')
        grupo = request.form.get('grupo')
        hora = request.form.get('hora')

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO asistencia (matricula, nombre_estudiante, folio_paciente, grupo, fecha, hora)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (matricula, nombre_estudiante, folio_paciente, grupo, fecha_actual, hora))
            conn.commit()
            flash('Asistencia registrada correctamente.', 'success')

        return redirect(url_for('asistencia'))

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asistencia")
        asistencias = cursor.fetchall()
    return render_template('asistencia.html', asistencias=asistencias, fecha_actual=fecha_actual)

# Ruta para eliminar un paciente
@app.route('/eliminar_paciente/<int:id>')
def eliminar_paciente(id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (id,))
        conn.commit()
    flash('Registro de paciente eliminado correctamente.', 'danger')
    return redirect(url_for('pacientes'))

# Ruta para descargar la base de datos
@app.route('/descargar')
def descargar():
    return send_file(DATABASE, as_attachment=True)

# Inicializar la base de datos
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
