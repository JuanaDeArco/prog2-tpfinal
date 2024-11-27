from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta,timezone
from . import app



# Función para generar un token JWT
def generate_token(username):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=3) # Token expira en 3 minutos
    token = jwt.encode({
        'username': username,
        'exp': expiration
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_token(token):
    """
    Decodifica el token jwt dato. Si se marcó que una secret_key esta expirada
    devuelve que se expiro el token
    Si se paso un token erroneo (por ej, algo generado con otra secret key)
    tira un invalid token
    """
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return 'Token expirado. Está rancio!'
    except jwt.InvalidTokenError:
        return 'Token inválido. Esta super rancio!'


def token_required(f):
 def decorated(*args, **kwargs):
    token = request.headers.get('Authorization') # Token se pasa en el encabezado
    app.logger.debug(f'token {token}')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        current_user = data['username']
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token!'}), 403
    return f(current_user, *args, **kwargs)
 return decorated