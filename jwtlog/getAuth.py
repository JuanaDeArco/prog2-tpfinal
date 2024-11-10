from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, render_template
import jwt #pip install pyjwt https://pyjwt.readthedocs.io/en/stable/
from User import Usuario
from GatronomicUser import UsuarioGastronomico
from PersonalUser import UsuarioPersonal
from menu_item import MenuItem
import csv
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'paginas'))

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'usuarios.txt')

# Este es la "private key" del jwt que se generen. Esto deberia estar afuera
# en un archivo de config o extraido desde una variable de entorno con os.environ
secret_key = 'Misecreto'

def generate_token(data):
    """
    Genera un token jwt usando la libreria jwt
    """
    token = jwt.encode(data, secret_key, algorithm='HS256')
    return token

def decode_token(token):
    """
    Decodifica el token jwt dato. Si se marcó que una secret_key esta expirada
    devuelve que se expiro el token
    Si se paso un token erroneo (por ej, algo generado con otra secret key)
    tira un invalid token
    """
    try:
        data = jwt.decode(token, secret_key, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return 'Token expirado. Está rancio!'
    except jwt.InvalidTokenError:
        return 'Token inválido. Esta super rancio!'


@app.route('/gettoken', methods=['POST'])
def gettoken():
    """
    Genero un token para un usuario y una contraseña
    De esta manera todas las otras request se hacen con ese token y no con un user y un pass
    """
    username = request.form.get('user')
    password = request.form.get('pass')
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for linea in reader:
            if linea[1] == username and linea[2] == password:
                user_type = linea[-1]
                print(user_type)
                token = generate_token({'username': username, 'password': password, "user_type" : user_type})
                response = jsonify({'token': token})
                response.headers['Location'] = url_for('perfil', token=token)
                return response, 302
            elif linea[1] == username:
                return jsonify({'message': 'Contraseña incorrecta'}), 403

    return jsonify({'message': 'Nombre de usuario no encontrado'}), 404


@app.route('/secreto', methods=['GET'])
def secreto():
    """
    Si no paso un token valido no puedo entrar acá
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No me diste un token!'}), 403

    token = token.replace('Bearer ', '')
    data = decode_token(token)

    if data == 'Token expirado. Está rancio!':
        return jsonify({'message': 'Token expirado. Está rancio!'}), 401
    elif data == 'Token inválido. Esta super rancio!':
        return jsonify({'message': 'Token inválido. Esta super rancio!'}), 401

    return jsonify({'message': 'Pudiste entrar a mi endpoint supersecreto!'})

if not os.path.exists(file_path):
    with open(file_path, 'w') as f:
        pass

@app.route('/') # esta no pide token :)
def hello():
    return send_from_directory(os.path.join(current_dir, 'paginas'), 'index.html')

@app.route('/login')
def login():
    return send_from_directory(os.path.join(current_dir, 'paginas'), 'login.html')

@app.route('/register')
def create_user_page():
    return send_from_directory(os.path.join(current_dir, 'paginas'), 'register.html')

@app.route('/register', methods=['POST'])
def crear_usuario():
    '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
    Esto más adelante va a ser una base de datos.
    Restricciones:
    - Todos los campos tienen que ser completados
    - La contraseña tiene que tener mínimo 6 caracteres
    - Para que el mail sea válido, tiene que tener un @ en algún lado
    - No se pueden repetir usuarios ni emails'''
    username = request.form.get("usuario")
    password = request.form.get("password") # ojo, se está guardando en texto plano
    email = request.form.get("email")
    user_type = request.form.get("user_type")
    
    if not username or not password or not email or not user_type:
        return jsonify({'message': 'Ningún campo puede estar vacío'}), 400
    if "@" not in email:
        return jsonify({'message': 'El correo electrónico debe tener un formato adecuado'}), 400
    if len(password) < 6:
        return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
    
    with open(file_path, 'r') as f: 
        lista = f.readlines()
        for linea in lista:
            if username in linea:
                return jsonify({'message': 'El nombre de usuario ya está siendo utilizado'}), 400
            if email in linea:
                return jsonify({'message': 'El correo electrónico ya está siendo utilizado'}), 400

    if user_type == 'gastronomico':
        usuario = UsuarioGastronomico(username=username, password=password, email=email)
    elif user_type == 'personal':
        usuario = UsuarioPersonal(username=username, password=password, email=email)
    else:
        return jsonify({'message': 'Tipo de usuario no válido'}), 400

    with open(file_path, 'a+') as f:
        f.write(f"{usuario.id},{usuario.username},{usuario.password},{usuario.email},{user_type}\n")
        return jsonify({'message': 'Usuario creado con éxito'}), 200

@app.route('/perfil')
def perfil():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Token no proporcionado'}), 403

    try:
        data = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_type = data['user_type']
        username = data['username']
        
        # Load user data from file
        with open(file_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for linea in reader:
                if linea[1] == username:
                    if user_type == 'personal':
                        user = UsuarioPersonal(username=linea[1], password=linea[2], email=linea[3])
                    else:
                        user = UsuarioGastronomico(username=linea[1], password=linea[2], email=linea[3])
                    break
        
        return render_template('perfil.html', user=user)
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token inválido'}), 403


if __name__ == '__main__':
    app.run(debug=True)
