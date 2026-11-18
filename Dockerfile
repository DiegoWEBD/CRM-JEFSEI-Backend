FROM python:3.14-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuario no privilegiado: la aplicación no corre como root.
# Los archivos subidos se escriben en /app/documentos (la app lo crea en runtime);
# si se monta un volumen en esa ruta, su dueño debe ser el usuario 'app'.
RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
