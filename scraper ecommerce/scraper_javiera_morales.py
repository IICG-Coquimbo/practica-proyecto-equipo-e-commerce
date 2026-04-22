from pymongo import MongoClient
import certifi
import urllib.parse

username ="Renato_Villalobos"
password =r"ubeiW7202\@@#%"
user_escaped = urllib.parse.quote_plus(username)
pass_escaped = urllib.parse.quote_plus(password)

uri = f"mongodb+srv://{user_escaped}:{pass_escaped}@cluster0.khaasrk.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(
    uri,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

try:
    print(client.server_info())
    print(" Conexi n exitosa")
except Exception as e:
    print(" Error:", e)

db = client["prueba"]
coleccion = db["personas"]

coleccion.insert_one({"nombre": "Vannessa", "edad": 30})

print(list(coleccion.find()))


import os
import time
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from tabulate import tabulate

def ejecutar_extraccion():
    datos_finales = []
    
    # --- CONFIGURACIÓN SELENIUM ---
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless") # Opcional: para que no se abra la ventana
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        pag_inicio = 4
        pag_fin = 7

        for pagina in range(pag_inicio, pag_fin + 1):
            url_actual = f"https://www.pcfactory.cl/categoria/computadores-y-tablets/notebooks?size=12&page={pagina}"
            driver.get(url_actual)
            
            # Esperar carga y scroll
            wait.until(EC.url_contains(f"page={pagina}"))
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            
            for i in range(1, 3):
                driver.execute_script(f"window.scrollTo(0, {i * 800});")
                time.sleep(2)

            # Localizar productos
            productos = driver.find_elements(By.CLASS_NAME, 'products__item')
            
            for p in productos:
                try:
                    nombre = p.find_element(By.CLASS_NAME, 'products__item__info__name').text.strip()
                    precio = p.find_element(By.CLASS_NAME, 'products__item__info__reference_price').text.strip()
                    
                    # Formato solicitado en la imagen
                    datos_finales.append({
                        "identificador": nombre,
                        "precio": precio,
                        "tienda": "PCfactory"  # Su identificador
                        "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S"),
                    })
                
                except Exception:
                    continue
                    
    finally:
        driver.quit()
    
    return datos_finales

# --- LÓGICA DE EJECUCIÓN Y MONGODB ---
if __name__ == "__main__":
    # Limpieza de procesos
    os.system("pkill -9 chrome || true")
    
    # Ejecutar la función
    resultados = ejecutar_extraccion()
    
    # Guardar en MongoDB si hay resultados
    if resultados:
        try:
            client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=5000)
            db = client['ecommerce']
            coleccion = db['notebooks_pcfactory']
            
            # Insertar los datos procesados
            for item in resultados:
                coleccion.update_one(
                    {'identificador': item['identificador']}, 
                    {'$set': item}, 
                    upsert=True
                )
            
            print(f"✅ Se procesaron e insertaron {len(resultados)} productos.")
            # Opcional: Mostrar tabla de lo extraído
            resumen = [[r['identificador'][:30], r['valor']] for r in resultados[:10]]
            print(tabulate(resumen, headers=["Producto", "Precio"], tablefmt="grid"))
            
        except Exception as e:
            print(f"❌ Error en base de datos: {e}")





