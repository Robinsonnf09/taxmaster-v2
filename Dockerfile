FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Debug: listar estrutura copiada
RUN ls -la /app && ls -la /app/templates || echo "Templates não encontrado"

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:\ --workers 1 app:app"]
