from flask import Flask

app = Flask(__name__) # app es el nombre de mi api y esto es "todo lo que viene ahora es la api"

@app.route('/') # ahora hay una ruta nueva en mi api, que es la raiz, y cuando haga un GET me va a correr la función que esta abajo de esto. si no le paso otro parametro, es un GET.
def hello():
    return 'Hello, World! desde el hello'

# para correr esto desde consola, flask --nombredemiapi nombredemiarchivo run --debug
# despues haremos el __init__ para que corra con un script
# mira esos comentarios de largo eterno, perdon pep8