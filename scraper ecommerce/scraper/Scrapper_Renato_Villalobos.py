import os
import time
import pytz
import random
from datetime import datetime
from pymongo import MongoClient

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def ejecutar_extraccion():
    # --- 1. LIMPIEZA DE PROCESOS ---
    try:
        os.system("pkill -9 chrome")
        os.system("pkill -9 chromedriver")
        os.system("rm -rf /tmp/.com.google.Chrome.*")
        os.system("rm -rf /tmp/.org.chromium.Chromium.*")
        print("🧹 Limpieza de procesos completada.")
    except:
        pass

    # --- 2. CONFIGURACIÓN GENERAL ---
    NOMBRE_GRUPO = "NotebookStoreCL"
    zona_chile = pytz.timezone('America/Santiago')
    datos_finales = []
    driver = None

    # --- 3. CONFIGURACIÓN DEL NAVEGADOR ---
    options = Options()
    # Si usas Docker, asegúrate de que esta ruta sea correcta
    if os.path.exists("/usr/bin/google-chrome"):
        options.binary_location = "/usr/bin/google-chrome"

    options.add_argument("--headless")  # Ejecución en segundo plano
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Uso de Service para evitar el error de "Unable to obtain driver"
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("🚀 Navegador iniciado correctamente.")

        # --- 4. EXTRACCIÓN ---
        limite_paginas = 4
        url_base = "https://notebookstore.cl/equipos/computadores/portatiles"
        
        for nivel_pagina in range(1, limite_paginas + 1):
            url_lista = f"{url_base}?page={nivel_pagina}"
            print(f"🔎 Procesando Página {nivel_pagina}: {url_lista}")
            driver.get(url_lista)

            # Esperar a que los productos carguen
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-block__name"))
                )
            except:
                print(f"⚠️ No se encontraron productos en la página {nivel_pagina}")
                break

            # Obtener URLs de productos de la página actual
            enlaces = driver.find_elements(By.CSS_SELECTOR, ".product-block__name")
            urls_productos = [e.get_attribute("href") for e in enlaces if e.get_attribute("href")]

            for url in urls_productos:
                try:
                    driver.get(url)
                    time.sleep(random.uniform(3, 5))

                    # Scroll para disparar lazy loading
                    driver.execute_script("window.scrollTo(0, 400);")
                    
                    # Extraer Nombre
                    nombre = driver.find_element(By.CSS_SELECTOR, ".product-page__title").text.strip()
                    
                    # Extraer Precio (Oferta/Transferencia suele ser el segundo)
                    precios_el = driver.find_elements(By.CSS_SELECTOR, ".custom-price-value")
                    precio_raw = precios_el[1].text if len(precios_el) > 1 else (precios_el[0].text if precios_el else "0")
                    
                    # Limpieza de precio a float
                    v_limpio = precio_raw.replace(".", "").replace(",", "").replace("$", "").replace("CLP", "").strip()
                    precio_final = float(v_limpio) if v_limpio.isdigit() else 0.0

                    # Extraer Specs
                    specs = {}
                    elementos_li = driver.find_elements(By.CSS_SELECTOR, "#producto_info_default ul li")
                    for li in elementos_li:
                        t = li.text.lower()
                        if any(x in t for x in ["intel", "amd", "ryzen", "core"]): specs["procesador"] = li.text
                        elif "ram" in t or "memoria" in t: specs["memoria ram"] = li.text
                        elif any(x in t for x in ["ssd", "nvme", "almacenamiento"]): specs["almacenamiento"] = li.text
                        elif '"' in t or "pantalla" in t: specs["pantalla"] = li.text
                        elif any(x in t for x in ["nvidia", "geforce", "rtx"]): specs["tarjeta de video"] = li.text

                    # Guardar datos
                    datos_finales.append({
                        "identificador": nombre,
                        "valor": precio_final,
                        "fecha_captura": datetime.now(zona_chile).strftime("%Y-%m-%d %H:%M:%S"),
                        "procesador": specs.get("procesador", "N/A"),
                        "almacenamiento": specs.get("almacenamiento", "N/A"),
                        "memoria ram": specs.get("memoria ram", "N/A"),
                        "pantalla": specs.get("pantalla", "N/A"),
                        "tarjeta de video": specs.get("tarjeta de video", "N/A"),
                        "grupo": NOMBRE_GRUPO,
                        "url": url
                    })
                    print(f"   ✅ {nombre[:35]}... - ${precio_final}")

                except Exception as e:
                    print(f"   ❌ Error en producto: {url} -> {e}")
                    continue

    except Exception as e:
        print(f" Error crítico en Selenium: {e}")
    finally:
        if driver:
            driver.quit()

    # --- 5. GUARDAR EN MONGODB ---
    if datos_finales:
        try:
            # Cambia 'mongodb' por 'localhost' si no usas Docker
            client = MongoClient("mongodb://mongodb:27017/", serverSelectionTimeoutMS=5000)
            db = client["ecommerce"]
            coleccion = db["G_ecommerce_scraping"]
            
            coleccion.insert_many(datos_finales)
            print(f"📦 Éxito: {len(datos_finales)} productos guardados en MongoDB.")
        except Exception as e:
            print(f"❌ Error al conectar con MongoDB: {e}")
    else:
        print("⚠️ No se extrajeron datos.")

    return datos_finales

# Ejecución
if __name__ == "__main__":
    ejecutar_extraccion()