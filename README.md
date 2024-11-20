# prog2-tpfinal
- Propuesta de negocios:

- User stories / requerimientos

- Diagrama UML

## Como instalar
Crear un entorno virtual:

`python -m venv venv`

Dentro del entorno:

`pip install -r requirements.txt`

Esto hace que se instalen todas las librerias listadas en el archivo `requirements.txt`.


## Como correr
Asumiendo que la carpeta que contiene el codigo se llama prog2-tpfinal, realizar en consola
```bash
cd prog2-tpfinal
python3 merendar.py
```
Esto va a arrancar la app en modo debug

La api esta en el path http://127.0.0.1:5000/api/v1/

### Como correr con docker
En el directorio donde esta el Dockerfile (deberia ser el raiz del repo)
```bash
docker build -t merendar:<version> .
```
donde `<version>` es el SEMVER que queremos de esa imagen
aca dejo un ejemplo para copiar y pegar
```bash
docker build -t merendar:0.1 .
```

Luego de eso, podemos hacer un 
```bash
docker run --volume=.:/app -p 8080:8080 merendar:0.1
```
* `--volume` nos permite marcar donde queremos que se monte la base de datos (si estamos usando sqlite, que es lo que usa default si no existe un mysql)

* `-p` es el puerto_contenedor:puerto_destino que exponemos. Como la api se buildea por defecto en el puerto 8080, necesitamos exponer ese puerto para poder usarlo desde el browser o postman

* merendar:0.1 es como tagueamos la version en el paso del docker build

## Requerimientos
Tiene que tener una base de datos andando

## Y Docker compose?
Podes ver lo de docker compose [aca](./compose.md)
