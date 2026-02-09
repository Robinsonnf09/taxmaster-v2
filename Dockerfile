FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Timestamp: 2026-02-08 22:23:52
RUN echo "Build timestamp: 2026-02-08 22:23:52"
RUN echo "=== CONTEUDO DE /app ===" && ls -la /app | head -20
RUN echo "=== CONTEUDO DE /app/templates ===" && ls -la /app/templates | head -20

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:8080 --workers 1 app:app
