from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from clickhouse_driver import Client
import clickhouse_connect
import socket
import threading

import time
import requests



def build_html_table(result):
    with open("table_template.html", "r") as file:
        template_content = file.read()
    
    # Construir las filas de la tabla
    result_rows = result.result_rows
    table_rows = ""
    for row in result_rows:
        table_rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    
    # Reemplazar {{table_rows}} en la plantilla con las filas generadas
    template_content = template_content.replace("{{table_rows}}", table_rows)
    return template_content

def enviar_resultado_bot():
    try:
        # Realizar la consulta a ClickHouse para obtener el total de registros
        client = clickhouse_connect.get_client(host='clickhouse', username='default', password='')
        query_total = "SELECT count() AS total FROM trips"
        result_total = client.query(query_total)
        total_data = result_total.result_rows[0][0]

        # Crear el mensaje a enviar al grupo de Telegram
        message = f"El total de registros en la tabla trips es: {total_data}"

        # URL de la API de Telegram para enviar mensajes
        
        # Enviar el mensaje al grupo de Telegram
        
        requests.post(f'https://api.telegram.org/bot6444843662:AAE2TciYCt1jnjNy-pgjM9IL8QaoG_EfXqc/sendMessage?chat_id=-1002122438815&text=Hola esta es la cantidad actual de datos en el DB {message}')
        print("Mensaje enviado correctamente")
           
    except Exception as e:
        print(f"Error al enviar el mensaje: {str(e)}")


def enviar_mensaje_recurrente():
    while True:
        enviar_resultado_bot()
        time.sleep(5)  # Envía el mensaje cada hora

# Inicia el hilo para enviar el mensaje recurrentemente
thread = threading.Thread(target=enviar_mensaje_recurrente)
thread.start()



app = FastAPI()

@app.get("/")
def read_root():
    #enviar_resultado_bot()
    return {"message": "Hola, este es mi microservicio con FastAPI y ClickHouse"}

@app.get("/consulta_clickhouse", response_class=HTMLResponse)
async def consulta_clickhouse(request: Request, per_page: int = Query(default=15, ge=1), page: int = Query(default=1, ge=1)):
    try:
        offset = (page - 1) * per_page
        socket.socket().connect(('pasantiatelconet-clickhouse-1', 8123))
        print("Conexión establecida correctamente")
        #enviar_resultado_bot() 
        print("hola")
        # Conéctate a ClickHouse
        client = clickhouse_connect.get_client(host='clickhouse', username='default', password='')
        
        query = f"""
        SELECT pickup_date, pickup_ntaname, SUM(1) AS number_of_trips 
        FROM trips 
        GROUP BY pickup_date, pickup_ntaname 
        ORDER BY pickup_date ASC 
        LIMIT {per_page} OFFSET {offset}
        """        
        query_total = """
        SELECT count() AS total FROM trips
        """
        print(query)
        result = client.query(query)
        result_total = client.query(query_total)
        total_data = result_total.result_rows[0][0]
        # Realiza una consulta de ejemplo
        html_content = build_html_table(result)
        # Recuperar el URL actual
        current_url = request.url
        current_page = page
        print(current_url)
        next_page = page + 1
         # Crear enlace a la siguiente página
        link = f"http://localhost:8000/consulta_clickhouse/?per_page={per_page}&page={next_page}"
        link_next = f'<a href="{link}">Enlace a la siguiente página</a>'
        template_content = html_content.replace("{{link}}", link_next)
        after_page = page - 1
         # Crear enlace a la siguiente página
        link = f"http://localhost:8000/consulta_clickhouse/?per_page={per_page}&page={after_page}"
        link_after = f'<a href="{link}">Enlace a la anterior página</a>'
        template_content = template_content.replace("{{link2}}", link_after)
        #result = client.execute("SELECT * FROM trips LIMIT 10")
        print(result)
        return HTMLResponse(content=template_content, headers={"X-Total-Count": str(total_data-per_page)})
    except Exception as e:
        return JSONResponse(content={"message": f"Error en la consulta: {str(e)}"}, status_code=500)







