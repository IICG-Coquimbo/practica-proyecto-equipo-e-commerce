import os
import time
import random
import re
import pytz
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ejecutar_extraccion_cintegral():
    # --- PASO 0: LIMPIEZA TOTAL Y REPARACIÓN ---
    os.system("pkill -9 chrome")
    os.system("pkill -9 chromedriver")
    os.system("rm -rf /tmp/.com.google.Chrome.*")
    os.system("rm -rf /tmp/.org.chromium.Chromium.*")
    print("🧹 Limpieza completada.")

    # --- VARIABLES GENERALES ---
    NOMBRE_TIENDA = "cintegral"
    zona_chile = pytz.timezone('America/Santiago')
    datos_finales = []
    driver = None

    # --- CONFIGURACIÓN DEL NAVEGADOR ---
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 - Proyecto Academico UCN")

    try:
        driver = webdriver.Chrome(options=options)
        print("🚀 Navegador iniciado correctamente.")

        # --- NAVEGACIÓN A LA URL DE NOTEBOOKS ---
        url_base = "https://cintegral.cl/categoria/pc-y-portatiles/notebook/"
        driver.get(url_base + "?count=36&paged=1")
        print(f"📄 Navegando a: {url_base}")

        time.sleep(random.uniform(8.5, 12.5))

        # Scroll suave para cargar productos
        for _ in range(3):
            driver.execute_script(f"window.scrollBy(0, {random.randint(300, 600)})")
            time.sleep(random.uniform(1, 2))

        # --- EXTRACCIÓN DE PRODUCTOS POR PÁGINA ---
        limite_paginas = 2  # Cambia según necesites
        
        for pagina in range(limite_paginas):
            print(f"\n--- Procesando Página {pagina + 1} ---")
            
            if pagina > 0:
                url_pagina = f"{url_base}?count=36&paged={pagina + 1}"
                driver.get(url_pagina)
                print(f"📄 Navegando a página {pagina + 1}")
                time.sleep(random.uniform(4, 6))
                driver.execute_script("window.scrollBy(0, 400)")
                time.sleep(2)
            
            # Esperar que carguen los productos
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3.porto-heading.post-title a"))
                )
            except:
                print("⚠️ Timeout esperando productos")
                continue

            # Extraer enlaces de productos
            enlaces_productos = driver.find_elements(By.CSS_SELECTOR, "h3.porto-heading.post-title a")
            urls_unicas = []
            for enlace in enlaces_productos:
                url = enlace.get_attribute("href")
                if url and url not in urls_unicas and "/producto/" in url:
                    urls_unicas.append(url)
            
            print(f"🔗 Encontrados {len(urls_unicas)} productos en esta página")

            # Procesar cada producto
            for idx, url_producto in enumerate(urls_unicas):
                try:
                    driver.get(url_producto)
                    time.sleep(random.uniform(3, 5))
                    
                    # --- EXTRAER TÍTULO (IDENTIFICADOR) ---
                    identificador = "No disponible"
                    try:
                        titulo_element = driver.find_element(By.CSS_SELECTOR, "h3.porto-heading.post-title")
                        identificador = titulo_element.text.strip()
                    except:
                        try:
                            titulo_element = driver.find_element(By.CSS_SELECTOR, "h1.product_title")
                            identificador = titulo_element.text.strip()
                        except:
                            identificador = "No disponible"
                    
                    # --- EXTRAER PRECIO ---
                    precio = 0
                    try:
                        precio_elem = driver.find_element(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi")
                        precio_texto = precio_elem.text.strip()
                        numeros = re.findall(r'[\d\.]+', precio_texto)
                        if numeros:
                            precio_limpio = numeros[0].replace(".", "")
                            precio = int(precio_limpio)
                    except:
                        try:
                            precio_elem = driver.find_element(By.CSS_SELECTOR, ".price .woocommerce-Price-amount")
                            precio_texto = precio_elem.text.strip()
                            numeros = re.findall(r'\d+', precio_texto)
                            if numeros:
                                precio = int(''.join(numeros))
                        except:
                            precio = 0
                    
                    print(f"✅ Producto: {identificador[:50]}... | Precio: ${precio:,}")
                    
                    # Guardamos SOLO los 4 campos requeridos
                    datos_finales.append({
                        "identificador": identificador,
                        "valor": precio,
                        "fecha_captura": datetime.now(zona_chile).strftime("%Y-%m-%d %H:%M:%S"),
                        "tienda": NOMBRE_TIENDA,
                        "url_fuente": url_producto  # Para evitar duplicados
                    })
                    
                    driver.back()
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"❌ Error en producto {idx + 1}: {str(e)[:80]}")
                    driver.get(url_base)
                    time.sleep(3)
                    continue

    except Exception as e:
        print(f"❌ Error en Selenium: {e}")
    finally:
        if driver:
            driver.quit()
            print("🔚 Navegador cerrado.")

    # --- GUARDAR EN MONGODB (SOLO 4 CAMPOS) ---
    try:
        print("\n💾 Conectando a MongoDB...")
        client = MongoClient("mongodb://mongodb:27017/", serverSelectionTimeoutMS=5000)
        db = client["ecommerce"]
        coleccion = db["G_ecommerce_scraping"]
        
        if datos_finales:
            for producto in datos_finales:
                coleccion.update_one(
                    {"url_fuente": producto["url_fuente"]},
                    {"$set": {
                        "identificador": producto["identificador"],
                        "precio": producto["valor"],
                        "fecha_captura": producto["fecha_captura"],
                        "tienda": producto["tienda"]
                    }},
                    upsert=True
                )
            print(f"✅ Datos guardados. Total: {len(datos_finales)} productos")
            
            # Mostrar muestra
            print("\n📋 MUESTRA DE DATOS GUARDADOS:")
            for i, prod in enumerate(datos_finales[:3]):
                print(f"  {i+1}. {prod['identificador'][:45]}...")
                print(f"     Precio: ${prod['valor']:,} | Tienda: {prod['tienda']}")
        else:
            print("⚠️ No hay datos para guardar.")
    except Exception as e:
        print(f"❌ Error en MongoDB: {e}")

    return datos_finales

if __name__ == "__main__":
    ejecutar_extraccion_cintegral()