import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

#### Clase de configuracion
### Aca ponemos la url de la base de datos, la clave secreta, etc
## Todo sale por variables de entorno (que van a estar en el contenedor de docker)
# Si tuvieramos multiples entornos podria ser una clase por cada uno
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    DEBUG = True
    
# app.secret_key = "cheesecake"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Luchi0803@127.0.0.1/test"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config['SECRET_KEY'] = 'ilovemerienda'
# app.config['SECURITY_PASSWORD_SALT'] = 'mUakkqoqoEAA9jB7yKg6ilOFnQdxxq9S'

    mysql_user=os.environ.get('MYSQL_USER')
    mysql_password=os.environ.get('MYSQL_PASSWORD')
    mysql_host=os.environ.get('DATABASE_URL')
    mysql_port=os.environ.get('DATABASE_PORT')
    mysql_database=os.environ.get('MYSQL_DATABASE')
    MYSQL=f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    print(MYSQL)
    SQLALCHEMY_DATABASE_URI = MYSQL or 'sqlite:///merendar.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'quegustotienelasal'
    # Tokens
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.urandom(24))
    user_secret = os.environ.get('USER_SECRET_KEY', os.urandom(24)) or os.urandom(24)
    ## Expiracion de los token
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
