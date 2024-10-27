# Usar Python 3.12 como imagen base
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt.txt
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y el archivo .env
COPY . .

# Exponer el puerto 3000
EXPOSE 3000

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]