### Que onda el Docker Compose

Docker Compose es una forma copada de administrar servicios de docker para deployar "un sólo servicio"

Lo ideal de una imagen de Docker es que sólo tenga una "cosa": una base de datos, un servidor web, el código de python, etc.

En el caso de esta api, tenemos "dos cosas"

* La api (el código)
* La base de datos

¿Podría fraccionar esto en más partes?: Totalmente, podría tener una imágen de docker que solo sirva los contenidos estáticos (las páginas web, las imágenes, etc), o incluso tener la API y el FRONTEND en contenedores separados. Mientras más atómico todo, más fácil es aislar posibles puntos de falla y facilita el deploy del servicio en la nube

Como esta ahora todo configurado, tenemos el `docker-compose.yml` con la declaración de la base de datos y la api.

## Componentes

* `docker-compose.yml`
  * Acá es el archivo de deploy. Tiene configurado el nombre del servicio, los volúmenes, redes y variables de entorno
* `.env`
  * Un archivo que tiene los valores que van a tener las variables de entorno que usa el servicio

### Por que tengo un archivo con contraseñas
Para evitar tener que meter las contraseñas en el código. Obviamente tampoco subo este archivo con contraseñas al repo, de hecho está en el `.gitignore` así nunca voy a subirlopor accidente. Dejo un archivo de "ejemplo" con un contenido de fantasía para mostrar como debería estar configurado.

docker compose, al momento de ser ejecutado, busca un archivo llamado `.env` en el mismo directorio donde está el `docker-compose.yml`, donde asume que están los valores de las variables que vas a usar en tu servicio.

Con esta leve intro, podes entender como usar docker-compose :)

Cuando aca hablamos de "servicio", nos referimos al deploy entero: la api y la base de datos.

## Como correr esta api usando docker-compose

### Requerimientos
* Tener docker
* Tener este repo clonado
* Opcional: [Mysql Workbench](https://dev.mysql.com/downloads/workbench/) para ver la base de datos

### Instrucciones

1. Clonamos el repo
  ```bash
git clone https://github.com/JuanaDeArco/prog2-tpfinal.git
```
2. Entramos al repo clonado
  ```bash
  cd prog2-tpfinal
  ```
3. Renombramos el archivo .env.ejemplo y colocamos ahi los datos que queremos
  ```bash
  mv .env.ejemplo .env
  ```
4. Arrancamos el deploy (*Nota*: tenes que tener docker encendido antes)
  ```bash
  docker compose up
  ```
Esto va a levantar el deploy en la consola mostrando los logs. Si quisieramos correr esto sin que nos ocupe la consola, podemos usar `docker compose up -d`

Para detener el servicio, podemos presionar `Ctrl + C` (y si usamos el -d, `docker compose stop`)

### Otros comandos de utilidad

* `docker compose down`
  * Destruye todo lo generado. Esto se usa para ir haciendo cambios y probando cambios en la api
* `docker compose up --build`
  * Vuelve a levantar el servicio recreando todo lo que hay en el docker-compose. Esto es para "buildear" de nuevo las imágenes de docker.
* `docker compose ps`
  * Lista cosas que haya corriendo como servicio de docker compose

## Expliame el docker compose
El contenido del docker-compose.yml se parece a esto
```yaml
services:
  mysql:
    build:
      context: ./db
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    networks:
      - merendar-network

  api:
    build:
      context: .
    depends_on:
      - mysql
    ports:
      - "8080:8080"
    environment:
      PORT: 8080
      DATABASE_URL: mysql
      DATABASE_PORT: ${DATABASE_PORT}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_PORT: 3306
      SECURITY_PASSWORD_SALT: ${SECURITY_PASSWORD_SALT}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      SECRET_KEY: ${SECRET_KEY}
    networks:
      - merendar-network


volumes:
  mysql-data:

networks:
  merendar-network: 
```
* `services` son los nombres de los contenedores, en nuestro caso, `mysql` para la base de datos y `api` para la api
* `build` y `context` son los parametros que le dicen a compose 'si tenes que buildear una Dockerfile, usa este contexto': Básicamente le dice donde tiene que pararse para buildear la imagen (si no sabe esto, comandos de un Dockerfile como el `COPY` no funcionan)
* `volumes` Indica volumenes que vn a usarse en los servicios: Esto se usa para la persistencia de la base de datos. Si no está esto, cuando apaguemos el servicio la base de datos deja de existir
* `environment` Son una lista de keys=values de variables de entorno
  * Estas variables son las que se usan en los servicios para pasar valores, como direcciones, nombres, contraseñas, números de puerto, etc.
  * Si nos fijamos en el código, es lo que despues se usa en 
  ```python
  os.environ.get("MI _VARABLE_DE_ENTORNO")
  ```
  * Se lee así: `MYSQL_DATABASE: ${MYSQL_DATABASE}`: A la izquierda del ":" tenemos el nombre de la variable de entorno (lo que buscamos con os.environ.get) y a la derecha el valor. Esto puede ser un valor fijo o algo `${entre llaves}` para indicar "esto viene del .env"
  * Algunas imágenes de Docker ya vienen con algunas como requerimiento (las dy MySql, por ejemplo). ¿De donde saqué como se llaman? de la documentación de la imágen de docker de MySql.
* `networks` Es la lista de redes que usan los servicios. Esto está para que ambos servicios estén en la misma "red" y se puedan ver
  * Si no esta esto, la api se rompe al momento de querer conectarse a la base de datos
* `ports` Es una lista de puertos que el servicio expone para poder ser usados.
  * MySql por ejemplo usa el 3306 para que se puedan conectar y nosotros elegimos usar el 8080 para la api.
  * Si no especificamos estos puertos, la api al conectarse al puerto 3306 de la base de datos fallaria, y nosotros al querer pegarle a la url o la api en el 8080 no andaría.
  * Esto se lee como "Puerto Interno: Puerto Externo". El puerto del contenedor (interno) se mapea al puerto del sistema (externo). 

## Explicame ahora el .env
El `.env` es un archivo bastante sencillo de leer: es una lista de `NOMBRE_DE_VARIALBES=valor_de_la_variable` que despues el servicio usa de alguna forma


## Cosas pendientes
Estaría bueno pasarle los secretos no como variables de entorno sinó como secretos