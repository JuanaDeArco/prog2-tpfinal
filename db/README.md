## Aca la base de datos

### Como buildear

```bash
docker build -f db/Dockerfile --build-arg MYSQL_ROOT_PASSWORD=admin123 --build-arg MYSQL_USER=ivana --build-arg MYSQL_PASSWORD=coso123 --build-arg MYSQL_DATABASE=merendar  -t sqlcontainer .
```

### Como correr
```bash
docker run -p 3306:3306 -v ./db/base:/var/lib/mysql sqlcontainer 
```

### Como testear la base de datos desde el mismo contenedor (si nuestra maquina no tiene mysql)
docker ps (lista contenedores corriendo; tiene que decir UP y listar un puerto en la seccion ports)
Copiar el container id
docker exec -ti containerid bash
Esto nos mete adentro del contenedor
mysql -h localhost -u usuario -p password dababase