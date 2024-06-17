from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cafeteria'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

autenticado = False  # Variable global para el estado de autenticación

# Definición del modelo de la base de datos


class Administra(db.Model):
    __tablename__ = 'administradores'
    gmail = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    n_identidad = db.Column(db.String(20), nullable=False)

    def __init__(self, nombre, gmail, contraseña, n_identidad):
        self.nombre = nombre
        self.gmail = gmail
        self.contraseña = contraseña
        self.n_identidad = n_identidad


class Empleado(db.Model):
    __tablename__ = 'empleados'
    gmail = db.Column(db.String(100), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    n_identidad = db.Column(db.String(20), nullable=False)

    def __init__(self, nombre, gmail, contraseña, n_identidad):
        self.nombre = nombre
        self.gmail = gmail
        self.contraseña = contraseña
        self.n_identidad = n_identidad


# Rutas y funciones de la aplicación Flask


@app.route('/')
def catalogo():
    user_name = session.get('user_name')
    logged_in = 'user_name' in session
    cargo = session.get('cargo', '')  # Obtener el cargo del usuario
    es_administrador = cargo == 'Administrador'

    print(f"Usuario en sesión: {user_name}, Logged in: {
          logged_in}, Cargo: {cargo}")  # Depuración

    return render_template('Catalogo.html', user_name=user_name, logged_in=logged_in, es_administrador=es_administrador, cargo=cargo)


# @app.route('/')
# def catalogo():
#     user_name = session.get('user_name')
#     logged_in = 'user_name' in session
#     print(f"Usuario en sesión: {user_name}, Logged in: {
#           logged_in}")  # Depuración
#     return render_template('Catalogo.html', user_name=user_name, logged_in=logged_in)


@app.route('/login', methods=['POST'])
def login():
    global autenticado
    email = request.form['email']
    password = request.form['password']
    print(f"Email recibido: {email}")  # Depuración
    print(f"Contraseña recibida: {password}")  # Depuración

    # Consultar la base de datos para encontrar el usuario por su email
    usuario = Administra.query.filter_by(gmail=email).first(
    ) or Empleado.query.filter_by(gmail=email).first()
    if usuario:
        print(f"Usuario encontrado: {usuario.gmail}")  # Depuración
        print(f"Contraseña en la base de datos: {
              usuario.contraseña}")  # Depuración
        # Si encontramos al usuario, verificamos su contraseña
        if usuario.contraseña == password:
            autenticado = True
            session['user_name'] = usuario.nombre
            if isinstance(usuario, Administra):
                session['cargo'] = 'Administrador'
            else:
                session['cargo'] = 'Empleado'
            print(f"Usuario autenticado: {session['user_name']}")  # Depuración
            print(f"Cargo del usuario: {session['cargo']}")  # Depuración
            return redirect(url_for('catalogo'))
        else:
            print("Contraseña incorrecta")  # Depuración
    else:
        print("Usuario no encontrado")  # Depuración

    # Si no se encontró al usuario o la contraseña es incorrecta
    flash('Correo o contraseña incorrectos')
    print("Autenticación fallida")  # Depuración
    return redirect(url_for('catalogo'))


@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('catalogo'))


@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    email = request.form['email']
    password = request.form['password']
    identidad = request.form['Identidad']
    cargo = request.form['cargo']

    print(f"Nombre recibido: {nombre}")  # Depuración
    print(f"Email recibido: {email}")  # Depuración
    print(f"Contraseña recibida: {password}")  # Depuración
    print(f"Identidad recibida: {identidad}")  # Depuración
    print(f"Cargo recibido: {cargo}")  # Depuración

    # Verificar si el usuario ya está registrado
    usuario_existente = Administra.query.filter_by(
        gmail=email).first() or Empleado.query.filter_by(gmail=email).first()
    if usuario_existente:
        flash('El usuario ya está registrado.')
        return redirect(url_for('catalogo'))

    # Crear un nuevo usuario dependiendo del cargo y guardar la contraseña sin encriptar en la base de datos
    if cargo == 'Administrador':
        nuevo_usuario = Administra(
            nombre=nombre, gmail=email, contraseña=password, n_identidad=identidad)
    else:
        nuevo_usuario = Empleado(
            nombre=nombre, gmail=email, contraseña=password, n_identidad=identidad)

    db.session.add(nuevo_usuario)
    db.session.commit()
    flash('Registro exitoso. ¡Ahora puedes iniciar sesión!')
    return redirect(url_for('catalogo'))


if __name__ == '__main__':
    app.run(debug=True)
