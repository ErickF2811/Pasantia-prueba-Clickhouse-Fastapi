from fastapi import FastAPI
from fastapi.responses import JSONResponse
from clickhouse_driver import Client
import clickhouse_connect



app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hola, este es mi microservicio con FastAPI y ClickHouse"}

@app.get("/consulta_clickhouse")
def consulta_clickhouse():
    try:
        print("hola")
        # Conéctate a ClickHouse
        client = clickhouse_connect.get_client(host='clickhouse', username='default', password='')
        #client.execute("USE default")

        # Realiza una consulta de ejemplo
        #result = client.execute("SELECT * FROM trips LIMIT 10")
        print("hola")
        return JSONResponse(content={"message": "Consulta exitosa", "data" : 1})
    except Exception as e:
        return JSONResponse(content={"message": f"Error en la consulta: {str(e)}"}, status_code=500)

