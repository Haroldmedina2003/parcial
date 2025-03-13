FROM python:3.9-slim

WORKDIR /app

# Copiar primero el archivo de dependencias
COPY requirements.txt .

# Actualizar pip y forzar instalación de numpy y pandas
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir numpy==1.23.5 pandas==2.0.3

# Instalar las demás dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API
COPY . .

# Comando para ejecutar la API
CMD ["python", "app.py"]
