from werkzeug.security import check_password_hash, generate_password_hash

# # Supongamos que has generado y almacenado la hash en la base de datos así:
# hashed_password = generate_password_hash('carlos123')
# print(hashed_password)
# # En el proceso de login, obtienes la contraseña ingresada por el usuario
# password = 'carlos123'

# # Verificas la contraseña ingresada contra la hash almacenada
# if check_password_hash(hashed_password, password):
#     print("Contraseña correcta")
# else:
#     print("Contraseña incorrecta")

# Código de prueba
hashed_password = generate_password_hash('fayoan')
print(hashed_password)
# print(check_password_hash(hashed_password, 'tu_contraseña_prueba'))

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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

    def __init__(self, nombre, gmail, contraseña):
        self.nombre = nombre
        self.gmail = gmail
        self.contraseña = generate_password_hash(contraseña)

# Rutas y funciones de la aplicación Flask


@app.route('/')
def catalogo():
    user_name = session.get('user_name')
    logged_in = 'user_name' in session
    print(f"Usuario en sesión: {user_name}, Logged in: {
          logged_in}")  # Depuración
    return render_template('Catalogo.html', user_name=user_name, logged_in=logged_in)


@app.route('/login', methods=['POST'])
def login():
    global autenticado
    email = request.form['email']
    password = request.form['password']
    print(f"Email recibido: {email}")  # Depuración
    print(f"Contraseña recibida: {password}")  # Depuración
    # Consultamos la base de datos para encontrar el usuario por su email
    usuario = Administra.query.filter_by(gmail=email).first()
    if usuario:
        print(f"Usuario encontrado: {usuario.gmail}")  # Depuración
        print(f"Contraseña en la base de datos: {
              usuario.contraseña}")  # Depuración
        # Desencriptar manualmente la contraseña almacenada en la base de datos
        if usuario.contraseña == password:  # Comparar la contraseña ingresada con la almacenada
            autenticado = True
            session['user_name'] = usuario.nombre
            print(f"Usuario autenticado: {session['user_name']}")  # Depuración
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
    print(f"Nombre recibido: {nombre}")  # Depuración
    print(f"Email recibido: {email}")  # Depuración
    print(f"Contraseña recibida: {password}")  # Depuración
    # Verificar si el usuario ya está registrado
    usuario_existente = Administra.query.filter_by(gmail=email).first()
    if usuario_existente:
        flash('El usuario ya está registrado.')
        return redirect(url_for('catalogo'))
    # Crear un nuevo usuario y guardar la contraseña encriptada en la base de datos
    nueva_contraseña_encriptada = generate_password_hash(password)
    nuevo_usuario = Administra(
        nombre=nombre, gmail=email, contraseña=nueva_contraseña_encriptada)
    db.session.add(nuevo_usuario)
    db.session.commit()
    flash('Registro exitoso. ¡Ahora puedes iniciar sesión!')
    return redirect(url_for('catalogo'))


if __name__ == '__main__':
    app.run(debug=True)
