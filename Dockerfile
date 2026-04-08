# Imagen base: trae Jupyter + Python + PySpark ya configurado
FROM jupyter/pyspark-notebook:latest

# Cambia al usuario administrador (root) para poder instalar programas
USER root

<<<<<<< Updated upstream
# 1. Actualiza repositorios e instala herramientas bï¿½sicas, instala Google Chrome y librerï¿½as necesarias
=======
# 1. Actualiza repositorios e instala herramientas básicas, instala Google Chrome y librerías necesarias
>>>>>>> Stashed changes
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates && \
    mkdir -p /etc/apt/keyrings && \
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y \
    google-chrome-stable \
    libnss3 \
    libgbm1 \
    libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
<<<<<<< Updated upstream
# 2. Instala librerï¿½as de Python necesarias
RUN pip install selenium pymongo webdriver-manager

# Vuelve al usuario normal de Jupyter (buena prï¿½ctica de seguridad)
USER jovyan
=======
# 2. Instala librerías de Python necesarias
RUN pip install selenium pymongo webdriver-manager

# Vuelve al usuario normal de Jupyter (buena práctica de seguridad)
USER jovyan
>>>>>>> Stashed changes
