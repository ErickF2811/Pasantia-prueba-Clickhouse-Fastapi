from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from clickhouse_driver import Client
import clickhouse_connect
import socket
import threading

import time
import requests



def build_html_table(result, barrios):
    with open("table_template.html", "r") as file:
        template_content = file.read()
    
    # Construir las filas de la tabla
    result_rows = result.result_rows
    table_rows = ""
    for row in result_rows:
        table_rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    
    # Reemplazar {{table_rows}} en la plantilla con las filas generadas
    template_content = template_content.replace("{{ table_rows }}", table_rows)

    # Renderizar la lista desplegable con los nombres de los barrios
    options = ""
    for barrio in barrios:
        options += f'<option value="{barrio}">{barrio}</option>'
    template_content = template_content.replace("{{ barrio_options }}", options)

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
        
        requests.post(f'https://api.telegram.org/bot6762754074:AAGYadTzU0lZaMDsZ8r0FdVckhfWN0YVx68/sendMessage?chat_id=-1002122438815&text=Hola esta es la cantidad actual de datos en el DB {message}')
        print("Mensaje enviado correctamente")
           
    except Exception as e:
        print(f"Error al enviar el mensaje: {str(e)}")


def enviar_mensaje_recurrente():
    while True:
        enviar_resultado_bot()
        time.sleep(3600/4)  # Envía el mensaje 15 min

# Inicia el hilo para enviar el mensaje recurrentemente
thread = threading.Thread(target=enviar_mensaje_recurrente)
thread.start()

def get_barrios():
    client = clickhouse_connect.get_client(host='clickhouse', username='default', password='')
    query_barrios = "SELECT DISTINCT pickup_ntaname FROM trips ORDER BY pickup_ntaname ASC"
    result_barrios = client.query(query_barrios)
    barrios = [row[0] for row in result_barrios.result_rows]
    return barrios


app = FastAPI()

@app.get("/")
def read_root():
    #enviar_resultado_bot()
    return {"message": "Hola, este es mi microservicio con FastAPI y ClickHouse"}


@app.get("/consulta_clickhouse", response_class=HTMLResponse)
async def consulta_clickhouse(request: Request, 
                              per_page: int = Query(default=15, ge=1), 
                              page: int = Query(default=1, ge=1),
                              pickup_ntaname: str = Query(default=None, description="Nombre del barrio"),
                              pickup_date: str = Query(default=None, description="Fecha de recogida")):
    try:
        offset = (page - 1) * per_page
        socket.socket().connect(('pasantia-prueba-clickhouse-fastapi-clickhouse-1', 8123))
        print("Conexión establecida correctamente")

        client = clickhouse_connect.get_client(host='clickhouse', username='default', password='')

        filters = ""
        f_pickup_ntaname = ""
        if pickup_ntaname:
            filters += f" AND pickup_ntaname = '{pickup_ntaname}'"
            f_pickup_ntaname += f"pickup_ntaname={pickup_ntaname}&"
        if pickup_date:
            filters += f" AND pickup_date = '{pickup_date}'"
            f_pickup_date += f"pickup_date={pickup_date}&"

        query = f"""
        SELECT pickup_date, pickup_ntaname, SUM(1) AS number_of_trips 
        FROM trips 
        WHERE 1 = 1 {filters}
        GROUP BY pickup_date, pickup_ntaname 
        ORDER BY pickup_date ASC 
        LIMIT {per_page} OFFSET {offset}
        """
        count_query = f"""SELECT count(*) FROM ({query}) AS subquery"""
        query_total = f"""
        SELECT count() AS total FROM trips
        WHERE 1 = 1 {filters}
        """

        print(query)
        result = client.query(query)
        result_total = client.query(query_total)
        total_data = result_total.result_rows[0][0]

        count_page = client.query(count_query)
        total_page = int(count_page.result_rows[0][0])
        print("el total de este query es " + str(total_page))
        barrios = get_barrios()

        html_content = build_html_table(result, barrios)

        current_url = str(request.url).split("?")[0]
        next_page = page + 1
        link = current_url + "?" + f_pickup_ntaname + f"per_page={per_page}&page={next_page}"
        link_next = f'<a href="{link}">Siguiente página</a>'

        after_page = page - 1
        link = current_url + "?"+ f_pickup_ntaname+f"per_page={per_page}&page={after_page}"
        link_after = f'<a href="{link}">Página anterior</a>'

        if total_page > 9:
            template_content = html_content.replace("{{ link }}", link_next)
        else:
            template_content = html_content.replace("{{ link }}", "")
            
        if page > 1:
            template_content = template_content.replace("{{ link2 }}", link_after)
        else:
            template_content = template_content.replace("{{ link2 }}", "")

        return HTMLResponse(content=template_content, headers={"X-Total-Count": str(total_data-per_page)})

    except Exception as e:
        return JSONResponse(content={"message": f"Error en la consulta: {str(e)}"}, status_code=500)






