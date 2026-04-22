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
import pytz
import random
import re
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================
# PASO 0: LIMPIEZA DE PROCESOS
# ============================================
os.system("pkill -9 chrome 2>/dev/null")
os.system("pkill -9 chromedriver 2>/dev/null")
print("Limpieza completada.")

# ============================================
# VARIABLES GENERALES
# ============================================
NOMBRE_GRUPO = "e-commerce"
zona_chile = pytz.timezone('America/Santiago')
URL_BASE = "https://todoclick.cl/notebook-477"
MAX_PAGINAS = 3
MAX_PRODUCTOS = 100
datos_finales = []
driver = None

def pausa_segura():
    time.sleep(random.uniform(3, 6))

def limpiar_precio(texto):
    if not texto:
        return 0
    numeros = re.findall(r'(\d{1,3}(?:\.\d{3})*|\d+)', texto)
    if numeros:
        return int(numeros[0].replace('.', ''))
    return 0

options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

try:
    driver = webdriver.Chrome(options=options)
    print("Navegador iniciado.\n")
    pausa_segura()
    
    # ============================================
    # EXTRAER LINKS
    # ============================================
    todos_links = []
    pagina_actual = 1
    
    while len(todos_links) < MAX_PRODUCTOS and pagina_actual <= MAX_PAGINAS:
        url_pagina = URL_BASE if pagina_actual == 1 else f"{URL_BASE}?page={pagina_actual}"
        print(f"Pagina {pagina_actual}: {url_pagina}")
        driver.get(url_pagina)
        pausa_segura()
        
        enlaces = driver.find_elements(By.CSS_SELECTOR, "a[href*='/notebooks/']")
        nuevos = 0
        for enlace in enlaces:
            href = enlace.get_attribute("href")
            if href and '/notebooks/' in href and href not in todos_links:
                if not any(x in href for x in ['-477', '-categoria', 'page=']):
                    todos_links.append(href)
                    nuevos += 1
        
        print(f"   Nuevos: {nuevos} | Total: {len(todos_links)}\n")
        
        if pagina_actual < MAX_PAGINAS:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, 'a[rel="next"], .pagination-next')
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                pausa_segura()
                driver.execute_script("arguments[0].click();", btn)
                pausa_segura()
                pagina_actual += 1
            except:
                break
        else:
            break
    
    todos_links = todos_links[:MAX_PRODUCTOS]
    print(f"Total productos a procesar: {len(todos_links)}\n")
    
    # ============================================
    # PROCESAR PRODUCTOS
    # ============================================
    for idx, url in enumerate(todos_links, 1):
        try:
            driver.get(url)
            pausa_segura()
            
            # NOMBRE
            nombre = "No especificado"
            try:
                nombre_elem = driver.find_element(By.CSS_SELECTOR, "h1.product_title, h1")
                nombre = nombre_elem.text.strip()
            except:
                pass
            
            # PRECIO
            precio = 0
            try:
                precio_elem = driver.find_element(By.CSS_SELECTOR, "span.precio-transferencia")
                precio = limpiar_precio(precio_elem.text)
            except:
                page_text = driver.page_source
                match = re.search(r'Pago Débito[:\s]*\$?\s*([\d\.]+)', page_text, re.IGNORECASE)
                if match:
                    precio = limpiar_precio(match.group(1))
            
            # ============================================
            # PRINT EN PANTALLA
            # ============================================
            print(f"[{idx}/{len(todos_links)}] Producto: {nombre[:50]} | Precio: ${precio:,}")
            
            # ============================================
            # DOCUMENTO PARA MONGODB (SOLO 4 CAMPOS)
            # ============================================
            documento = {
                "identificador": nombre,
                "precio": precio,
                "tienda": "TodoClick",
                "fecha_captura": datetime.now(zona_chile).strftime("%Y-%m-%d %H:%M:%S")
            }
            datos_finales.append(documento)
            
        except Exception as e:
            print(f"[{idx}] Error: {e}")
            continue
    
    print(f"\nTotal capturado: {len(datos_finales)} productos")

except Exception as e:
    print(f"Error general: {e}")

finally:
    if driver:
        driver.quit()
        print("Navegador cerrado.")

# ============================================
# GUARDAR EN MONGODB (SOLO 4 CAMPOS)
# ============================================
if datos_finales:
    try:
        client = MongoClient("mongodb://mongodb:27017/", serverSelectionTimeoutMS=5000)
        db = client["ecommerce"]
        coleccion = db["G_ecommerce_scraping"]
        coleccion.insert_many(datos_finales)
        print(f"\n{len(datos_finales)} productos guardados en MongoDB")
        print(f"Campos guardados: identificador, precio, tienda, fecha_captura")
    except Exception as e:
        print(f"Error MongoDB: {e}")
else:
    print("No hay datos para guardar")