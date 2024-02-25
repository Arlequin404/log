from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='template')
app.secret_key = "grupo6"

# Configuración de SQLAlchemy para conectar con MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/login'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)


class Aula(db.Model):
    __tablename__ = 'aulas'
    id_materia = db.Column(db.Integer, primary_key=True)
    nombre_materia = db.Column(db.String(100), nullable=False)
    curso = db.Column(db.String(50))
    fecha = db.Column(db.Date)
    descripcion = db.Column(db.Text)


class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    id_calificacion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_materia = db.Column(db.Integer, db.ForeignKey('aulas.id_materia'))
    calificacion = db.Column(db.Float)
    fecha_calificacion = db.Column(db.Date)

    usuario = db.relationship("Usuario", backref="calificaciones")
    aula = db.relationship("Aula", backref="calificaciones")


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        # Consulta en la base de datos utilizando SQLAlchemy
        account = Usuario.query.filter_by(correo=_correo, password=_password).first()

        if account:
            session['logueado'] = True
            session['id_usuario'] = account.id_usuario
            return render_template("index.html")
        else:
            return render_template('login.html', mensaje="Usuario o Contraseña Incorrectas")
    else:
        return render_template('login.html')


@app.route('/aulas')
def listar_aulas():
    aulas = Aula.query.all()
    return render_template('aulas.html', aulas=aulas)


@app.route('/aulas/nueva', methods=['GET', 'POST'])
def nueva_aula():
    if request.method == 'POST':
        nombre_materia = request.form['nombre_materia']
        curso = request.form['curso']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        nueva_aula = Aula(nombre_materia=nombre_materia, curso=curso, fecha=fecha, descripcion=descripcion)
        db.session.add(nueva_aula)
        db.session.commit()
        return redirect(url_for('listar_aulas'))
    return render_template('nueva_aula.html')


@app.route('/aulas/<int:id>/editar', methods=['GET', 'POST'])
def editar_aula(id):
    aula = Aula.query.get_or_404(id)
    if request.method == 'POST':
        aula.nombre_materia = request.form['nombre_materia']
        aula.curso = request.form['curso']
        aula.fecha = request.form['fecha']
        aula.descripcion = request.form['descripcion']
        db.session.commit()
        return redirect(url_for('listar_aulas'))
    return render_template('editar_aula.html', aula=aula)


@app.route('/aulas/<int:id>/eliminar', methods=['POST'])
def eliminar_aula(id):
    aula = Aula.query.get_or_404(id)

    # Eliminar las calificaciones relacionadas
    Calificacion.query.filter_by(id_materia=aula.id_materia).delete()

    # Eliminar el aula
    db.session.delete(aula)
    db.session.commit()

    return redirect(url_for('listar_aulas'))


@app.route('/crud_aulas')
def crud_aulas():
    return render_template('crud_aulas.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        correo = request.form['correo']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        password = request.form['password']
        rol = request.form['rol']

        # Verificar si el correo ya está registrado
        if Usuario.query.filter_by(correo=correo).first():
            return 'El correo electrónico ya está registrado.'

        # Crear un nuevo usuario
        nuevo_usuario = Usuario(correo=correo, nombre=nombre, apellido=apellido, password=password, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('registro.html')


@app.route('/atras')
def atras():
    return redirect(url_for('listar_aulas'))


@app.route('/logout', methods=['POST'])
def cerrar_sesion():
    # Lógica para cerrar sesión aquí
    session.clear()  # Por ejemplo, limpiar la sesión

    # Redirigir a la página de inicio de sesión o a donde quieras después de cerrar sesión
    return redirect(url_for('login'))


@app.route('/calificaciones')
def calificaciones():
    # Verificar si el usuario está logueado
    if 'logueado' not in session:
        return redirect(url_for('login'))

    # Obtener el ID de usuario de la sesión
    id_usuario = session.get('id_usuario')

    # Consultar las calificaciones del usuario actual
    calificaciones_usuario = Calificacion.query.filter_by(id_usuario=id_usuario).all()

    return render_template('calificaciones.html', calificaciones=calificaciones_usuario)


@app.route('/guardar_calificacion', methods=['POST'])
def guardar_calificacion():
    if request.method == 'POST':
        aula_id = request.form['aula']
        calificacion = request.form['calificacion']

        # Aquí puedes procesar los datos del formulario y guardar la calificación en la base de datos
        # Por ejemplo:
        nueva_calificacion = Calificacion(aula_id=aula_id, calificacion=calificacion)
        db.session.add(nueva_calificacion)
        db.session.commit()

        # Después de guardar la calificación, puedes redirigir a la página de calificaciones o a donde desees
        return redirect(url_for('calificaciones'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)
