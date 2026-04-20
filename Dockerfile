# --------- BUILD STAGE ---------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

# --------- RUNTIME STAGE ---------
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# copiar dependencias instaladas
COPY --from=builder /install /usr/local

# copiar código
COPY --from=builder /app /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
