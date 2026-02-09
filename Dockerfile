FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Debug: verificar se templates foi copiado
RUN echo "=== ARQUIVOS EM /app ===" && ls -la /app
RUN echo "=== ARQUIVOS EM /app/templates ===" && ls -la /app/templates

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:8080 --workers 1 app:app
