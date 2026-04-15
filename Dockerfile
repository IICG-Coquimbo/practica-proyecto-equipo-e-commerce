# Imagen base con Jupyter + PySpark (Spark 3.5.x)
FROM jupyter/pyspark-notebook:latest

USER root

<<<<<<< HEAD
# 1. Instalación de dependencias del sistema y entorno visual
=======
<<<<<<< HEAD
# 1. Actualiza repositorios e instala herramientas bï¿½sicas, instala Google Chrome y librerï¿½as necesarias
=======
# Instala entorno visual, supervisor y Chrome
>>>>>>> 3d5e9cb7c5d6b90831e8ee1a9430709166f500d6
>>>>>>> 17402e219efe418d9f447b1decfe5b0277837a3b
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    python3-websockify \
    novnc \
    libnss3 \
    libgbm1 \
<<<<<<< HEAD
    libasound2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
# 2. Instala librerï¿½as de Python necesarias
RUN pip install selenium pymongo webdriver-manager

# Vuelve al usuario normal de Jupyter (buena prï¿½ctica de seguridad)
USER jovyan
=======
    libasound2 \
    sed \
    && mkdir -p /etc/apt/keyrings \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalación de JARs: Versión 10.3.0 (Compatible con Spark 3.5)
# Limpiamos la carpeta primero para que no queden versiones viejas chocando
RUN rm -f /usr/local/spark/jars/mongo-spark-connector* && \
    rm -f /usr/local/spark/jars/mongodb-driver* && \
    rm -f /usr/local/spark/jars/bson*

RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar -P /usr/local/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/mongodb/bson-record-codec/4.11.1/bson-record-codec-4.11.1.jar -P /usr/local/spark/jars/

# 3. Instalación de librerías Python
RUN pip install selenium pymongo webdriver-manager pandas

# 4. Configuración de entorno y archivos
ENV DISPLAY=:99
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh \
    && chmod +x /usr/local/bin/start-vnc.sh && \
    chown -R jovyan:users /home/jovyan/work

EXPOSE 8888 5900 6080 4040

<<<<<<< HEAD
# Iniciamos como root para evitar el error de setuid de la sesión anterior
USER root
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
=======
# Inicia supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
>>>>>>> 3d5e9cb7c5d6b90831e8ee1a9430709166f500d6
>>>>>>> 17402e219efe418d9f447b1decfe5b0277837a3b
