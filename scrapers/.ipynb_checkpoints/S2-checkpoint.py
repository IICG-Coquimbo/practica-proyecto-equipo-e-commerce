<<<<<<< HEAD
def scraper_kiwoko(driver, By, paginas=1):
    datos_tienda = []
    base_url = "https://www.kiwoko.com/perros/comida-para-perros/dietas-veterinarias/"
    wait = WebDriverWait(driver, 20)

    for p in range(1, paginas + 1):
        url = f"{base_url}?p={p}" if p > 1 else base_url
        print(f"   [Kiwoko] Extrayendo datos de página {p}...")
        try:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.isk-product-card, .product-tile")))

            script_js = """
            let items = document.querySelectorAll('div.isk-product-card, .product-tile');
            return Array.from(items).map(item => ({
                sku_id: item.querySelector('a.isk-product-card__title, .product-name, h3')?.innerText.trim() || "Sin nombre",
                precio_raw: item.querySelector('.isk-product-card__price, .price-value')?.getAttribute('data-min-price') || "0.0",
                marca: item.querySelector('.brand-name, .isk-product-card__brand')?.innerText.trim() || "S/M",
                formato_raw: item.querySelector('.isk-product-card__pum, .product-format')?.innerText.trim() || ""
            }));
            """
            items = driver.execute_script(script_js)

            for item in items:
                datos_tienda.append({
                    "sku_id": item['sku_id'],
                    "marca": item['marca'],
                    "precio_raw": item['precio_raw'],
                    "formato_raw": item['formato_raw'] if item['formato_raw'] else item['sku_id'],
                    "tienda": "Kiwoko",
                    "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"   ⚠️ Error Kiwoko P{p}: {e}")
=======
import time
import datetime

def scraper_kiwoko(driver, By, paginas=1):
    datos_tienda = []
    base_url = "https://www.kiwoko.com/perros/comida-para-perros/dietas-veterinarias/"
    
    for p in range(1, paginas + 1):
        url = f"{base_url}?p={p}" if p > 1 else base_url
        try:
            driver.get(url)
            # 1. Scroll para disparar el renderizado de datos (Lazy Load)
            driver.execute_script("window.scrollTo(0, 600);") 
            time.sleep(3) # Espera necesaria para que los datos "reales" reemplacen al esqueleto

            # 2. JS optimizado con validación de existencia de datos
            script_js = """
            let items = document.querySelectorAll('div.isk-product-card');
            return Array.from(items).map(item => {
                let headline = item.querySelector('.isk-product-card__headline');
                let brand_el = item.querySelector('.isk-product-card__headline-brand');
                
                let marca_real = brand_el ? brand_el.innerText.trim() : "S/M";
                let nombre_real = headline ? headline.childNodes[headline.childNodes.length - 1].textContent.trim() : "Sin nombre";
                
                let precio = item.querySelector('.isk-product-card__price')?.getAttribute('data-min-price') || "0.0";
                let opciones = item.querySelector('.isk-product-card__pum')?.innerText.trim() || "";
                let rating = item.querySelector('.isk-reviews')?.getAttribute('data-rating') || "0";
                let opiniones = item.querySelector('.isk-product-card__reviews-total')?.innerText.replace(/[()]/g, "").trim() || "0";
                let sku_real = item.getAttribute('data-itemid') || nombre_real;

                return {
                    sku_id: sku_real,
                    marca: marca_real,
                    precio_raw: precio,
                    formato_raw: nombre_real + " " + opciones,
                    rating: rating,
                    opiniones: opiniones,
                    moneda: "EUR"
                };
            });
            """
            items = driver.execute_script(script_js)

            # 3. Filtrado de Veracidad: No enviar registros que no tengan precio o nombre real
            for item in items:
                if item['precio_raw'] != "0.0" and item['sku_id'] != "Sin nombre":
                    item["tienda"] = "Kiwoko"
                    item["fecha_captura"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    datos_tienda.append(item)
            
            print(f"✅ Kiwoko P{p}: {len(items)} detectados, {len(datos_tienda)} válidos.")

        except Exception as e:
            print(f"⚠️ Error Kiwoko P{p}: {e}")
>>>>>>> 02ff291445325a8dcf9218487415fae09ceaa93f
            continue
            
    return datos_tienda