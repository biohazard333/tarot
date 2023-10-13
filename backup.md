# Imagen base de Python
FROM python:3.9-slim-buster

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8501 para la aplicación Streamlit
EXPOSE 8501

# Ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "app.py"]
