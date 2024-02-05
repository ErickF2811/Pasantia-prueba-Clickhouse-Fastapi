FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install uvicorn  # Asegúrate de que uvicorn esté instalado
RUN pip install clickhouse_connect
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
