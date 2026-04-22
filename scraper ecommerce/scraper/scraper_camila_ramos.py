import os
import time
import re
import shutil # Para limpiar carpetas
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

def ejecutar_extraccion():
    # 1. LIMPIEZA RADICAL DE PROCESOS Y CACHÉ VIEJA
    os.system("pkill -9 brave")
    os.system("pkill -9 chromedriver")
    
    # Esto borra la carpeta donde webdriver-manager guarda los drivers viejos (v114)
    cache_path = os.path.expanduser("~/.wdm")
    if os.path.exists(cache_path):
        shutil.rmtree(cache_path)
        print("🧹 Caché de drivers antiguos eliminada.")

    # 2. CONFIGURACIÓN DE OPCIONES
    options = Options()
    options.binary_location = "/usr/bin/brave-browser"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = None
    try:
        print("⏳ Descargando driver actualizado para Brave v147...")
        
        # Usamos ChromeType.CHROMIUM para que sea compatible con Brave
        # El manager ahora buscará la versión más reciente disponible (v147 aprox)
        path_driver = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        
        service = Service(executable_path=path_driver)
        driver = webdriver.Chrome(service=service, options=options)
        print("🚀 Navegador iniciado con éxito.")

        # --- LÓGICA DE EXTRACCIÓN ---
        datos_finales = []
        driver.get("https://listado.mercadolibre.cl/notebook")

        for nivel_pagina in range(2):
            print(f"📄 Procesando Página {nivel_pagina + 1}...")
            time.sleep(5)

            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "poly-card"))
            )

            bloques = driver.find_elements(By.CLASS_NAME, "poly-card")

            for bloque in bloques:
                try:
                    nombre = bloque.find_element(By.CLASS_NAME, "poly-component__title").text
                    precio_texto = bloque.find_element(By.CLASS_NAME, "poly-price__current").text

                    v_limpio = precio_texto.replace("$", "").replace(".", "").replace(",", "").replace("\n", "").strip()
                    solo_numeros = re.findall(r'\d+', v_limpio)
                    precio_final = float(solo_numeros[0]) if solo_numeros else 0.0

                    datos_finales.append({
                        "identificador": nombre,
                        "valor": precio_final,
                        "grupo": "Soto_Team",
                        "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "tienda": "MercadoLibre"
                    })
                except Exception:
                    continue

            # Avanzar página
            try:
                boton = driver.find_element(By.CSS_SELECTOR, "a.andes-pagination__link[title='Siguiente']")
                driver.execute_script("arguments[0].click();", boton)
            except:
                break
        
        return datos_finales

    except Exception as e:
        print(f"❌ Error en Selenium: {e}")
        return []
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    resultados = ejecutar_extraccion()
    print(f"✅ Extracción terminada: {len(resultados)} productos.")

    if resultados:
        try:
            # "mongodb" debe ser el nombre del contenedor en tu docker-compose
            client = MongoClient("mongodb", 27017, serverSelectionTimeoutMS=5000)
            db = client["prueba"]
            db.ecommerce.insert_many(resultados)
            print("💾 Datos guardados en MongoDB correctamente.")
        except Exception as e:
            print(f"❌ Error en MongoDB: {e}")