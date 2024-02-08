
# README

Este repositorio contiene los scripts y configuraciones necesarios para implementar un conjunto de servicios utilizando Docker Compose. Se despliegan un nodo de ClickHouse y un nodo de ClickHouse Keeper en contenedores Docker, junto con un microservicio en Python utilizando FastAPI, que se conecta a la base de datos ClickHouse.

## Requerimientos

### 1. ClickHouse y ClickHouse Keeper

Se levanta un nodo de ClickHouse y uno de ClickHouse Keeper en contenedores Docker. Los archivos de configuración se encuentran en `docker-compose.yml`.

```plaintext
[Imagen de ClickHouse y ClickHouse Keeper]
```

### 2. Cargar datos de ejemplo

Se carga la información de ejemplo desde [Advanced Tutorial](https://clickhouse.tech/docs/en/getting_started/example_datasets/). Esto incluye la creación de la tabla `trips` con una estructura específica y la carga de aproximadamente 2 millones de registros.

### 3. Microservicio con FastAPI

Se crea un microservicio en Python utilizando FastAPI, implementando un API REST para interactuar con la base de datos de ClickHouse.

Se incluyen las dependencias necesarias en el archivo `requirements.txt`.

```plaintext
[Imagen de FastAPI]
```

### 4. API REST del microservicio

El API REST del microservicio ofrece los siguientes recursos:

- Todas las carreras realizadas, ordenadas por fecha de recogida.
- El número diario de recogidas por barrio.

La paginación se configura por defecto con 15 registros por página y se puede modificar mediante parámetros de consulta.

### 5. Documentación del API

El microservicio cuenta con documentación automática generada por FastAPI, siguiendo el estándar OpenAPI.

### 6. Actividad programada

El microservicio realiza una actividad programada cada quince minutos, consultando el total de registros en la tabla `trips` y enviando el resultado a un grupo de Telegram.

Se asegura el manejo adecuado de secretos y datos sensibles.

## Uso

1. Clona este repositorio.
2. Ejecuta `docker-compose up --build` para levantar los servicios.
3. Accede a `http://localhost:8000/docs` para interactuar con el API del microservicio.

## Estructura del repositorio

- `docker-compose.yml`: Configuración de los servicios Docker.
- `Dockerfile`: Configuración del contenedor para el microservicio.
- `main.py`: Código del microservicio FastAPI.
- `requirements.txt`: Dependencias del microservicio.
- `script.sql`: Instrucciones SQL para crear la tabla `trips` y cargar datos de ejemplo.

## Contribución

Las contribuciones son bienvenidas. Si tienes sugerencias o encuentras algún problema, por favor abre un *issue*.

---

Este README fue generado automáticamente.