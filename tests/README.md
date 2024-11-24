## Aca estan los tests

## Model Tests
Estos son los tests de las tablas de las bases de datos
Son bastante básicos pero como no vimos tests tampoco profundicé demasiado

Al momento de correr, se crea una base local (no mysql, crea un sqlite),crea las cosas y luego las borra al finalizar cada tests

### Mejoras
Claramente faltarian mas tests de los modelos: que pasa si en cada tabla se suben valores incorrectos (una string en vez de integer, etc)


## Api Tests
Acá hay algunos tests de endpoints.
Tanto como para la API en si (/api/meriendas/endpoint) como para el sitio

Los tests del sitio son bastante triviales (aseguran que se devuelva un 200)
Los de la api pueden animarse a ser mas interesantes, creando objetos y revisando que puede pasar si paso datos mal


## Como corro los tests
Desde el vscode es correr los tests desde el plugin de pytests

Sino, desde la consola podes escribir

```
cd prog2-tpfinal
pytest
```
pytest va a descubrir solo los testings (estan en la carpeta `tests` y los scripts que tienen tests empiezan con `test_`)

## Errores conocidos
```
LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy and becomes a legacy construct in 2.0. The method is now available as Session.get() (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    fetched_picture = ProfilePicture.query.get(profile_picture.id)
```
