import jwt

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

