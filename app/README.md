## Aca esta la API en si

### Como buildear

```bash
docker build  --build-arg PORT=8080 -t "pythonapi:1" .
```
Donde pythonapi es el nombre de la imagen y 1 es la version

### Como correr
```bash
docker run -p 8080:8080 pythonapi:1  
```


### Como crear el requirements.txt
```bash
pip freeze > requirements.txt
```
Esto hace que se cree el archivo con todas las dependencias y sus versiones