from flask import Flask, request, jsonify
import jwt #pip install pyjwt https://pyjwt.readthedocs.io/en/stable/
from usuario import Usuario
import csv

app = Flask(__name__)

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
    username = request.headers.get('user')
    password = request.headers.get('pass')
    f = csv.reader(open('usuarios.txt', 'r'), delimiter=',')
    find = False    
    for linea in f:
        if username in linea:
            find = True
            if password not in linea:
                return jsonify({'message': 'Contraseña incorrecta'}), 403

    if find == False:    
        return jsonify({'message': 'Nombre de usuario no encontrado'}), 404
    
    token = generate_token({'username': username, 'password': password})
    return jsonify({'token': token})

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

def cant_usuarios(archivo):
    # esta funcion se va a reemplazar por una consulta a la DB
    '''Como cada usuario es una linea en un archivo de texto, cuenta los usuarios contando las lineas'''
    with open(archivo, 'r') as f:
        return len(f.readlines())

@app.route('/create_user', methods=['POST'])
def crear_usuario():
    '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
    Esto mas adelante va a ser una base de datos.
    Restricciones:
    - Todos los campos tienen que ser completados
    - La contraseña tiene que tener minimo 6 carcteres
    - Para que el mail sea válido, tiene que tener un @ en algún lado
    - Se pueden repetir mails y contraseñas, pero no usuarios'''
    username = request.headers.get("usuario")
    password = request.headers.get("password") # ojo, se esta guardando en texto plano
    email = request.headers.get("email")
    if username == '' or password == '' or email == '':
        return jsonify({'message': 'Ningún campo puede estar vacío'}), 400
    if not "@" in email:
        return jsonify({'message': 'El correo electrónico debe tener un formato adecuado'}), 400
    if len(password) < 6:
        return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
    with open('usuarios.txt', 'r') as f: #chequeo de usuario unico. esto es muy burdo pero como es un ejemplo servirá.
        lista = f.readlines()
        for linea in lista:
            if linea.find(username) != -1:
                return jsonify({'message': 'El nombre de usuario ya está siendo utilizado'}), 400

    with open('usuarios.txt', 'a+') as f:
        usuario = Usuario(cant_usuarios('usuarios.txt'), username, password, email)
        f.write(f"{usuario.id},{usuario.username},{usuario.password},{usuario.email}\n")
        return jsonify({'message': 'Usuario creado con éxito'}), 200


@app.route('/') # esta no pide token :)
def hello():
    return "Hola Mundo! aca en esta api este es el único endpoint, no hay ninguno más! posta!"

if __name__ == '__main__':
    app.run(debug=True)
