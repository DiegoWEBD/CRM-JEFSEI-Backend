FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade "certifi>=2026.10.19" 

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]