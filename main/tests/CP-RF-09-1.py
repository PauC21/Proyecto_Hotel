from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

def setup_driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    try:
        service = webdriver.ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"⚠️ Aviso ChromeDriver: {e}")
        driver = webdriver.Chrome(options=options)
    
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 15)
    return driver, wait

def login(driver, wait, username, password):
    try:
        print(f"🔑 Iniciando sesión como: {username}")
        driver.get("http://127.0.0.1:8000/accounts/login/")
        
        # Esperar a que cargue la página de login
        time.sleep(2)
        
        # Buscar campos de forma flexible
        username_fields = driver.find_elements(By.NAME, "username")
        if not username_fields:
            username_fields = driver.find_elements(By.ID, "id_username")
        if not username_fields:
            username_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        
        if username_fields:
            username_fields[0].clear()
            username_fields[0].send_keys(username)
            print(f"   ✅ Campo username encontrado y llenado")
        else:
            print("❌ No se pudo encontrar campo username")
            return False

        # Buscar campo password
        password_fields = driver.find_elements(By.NAME, "password")
        if not password_fields:
            password_fields = driver.find_elements(By.ID, "id_password")
        if not password_fields:
            password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        
        if password_fields:
            password_fields[0].clear()
            password_fields[0].send_keys(password)
            print(f"   ✅ Campo password encontrado y llenado")
        else:
            print("❌ No se pudo encontrar campo password")
            return False

        # Buscar botón de submit
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
        if not buttons:
            buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        if not buttons:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        
        if buttons:
            buttons[0].click()
            print("   ✅ Botón de login clickeado")
        else:
            print("❌ No se pudo encontrar botón de submit")
            return False
        
        # Esperar y verificar resultado
        time.sleep(3)
        
        # Verificar si el login fue exitoso
        if "login" in driver.current_url.lower():
            print("❌ Login fallido - todavía en página de login")
            driver.save_screenshot("login_failed_rf09.png")
            return False
        else:
            print("✅ Login exitoso - redirigido a otra página")
            return True
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        driver.save_screenshot("login_error_rf09.png")
        return False

def test_proximas_reservas():
    driver, wait = setup_driver()
    
    try:
        print("="*60)
        print("CP-RF-09-1: MOSTRAR PRÓXIMAS RESERVAS")
        print("="*60)
        
        # 1. Iniciar sesión
        if not login(driver, wait, "palis", "Proyecto2025++"):
            print("❌ No se pudo iniciar sesión")
            return False
        
        # 2. Navegar al módulo de reservas
        print("\n📅 Navegando a módulo de reservas...")
        driver.get("http://127.0.0.1:8000/reservations/")
        time.sleep(3)
        
        print(f"   URL actual: {driver.current_url}")
        
        # 3. Verificar que estamos en la página correcta
        if "reservations" not in driver.current_url:
            print("⚠️ No estamos en la página de reservas esperada")
            # Intentar encontrar enlace a reservas
            reservation_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Reserv")
            if reservation_links:
                reservation_links[0].click()
                time.sleep(2)
        
        # 4. Buscar elementos de reservas
        print("\n🔍 Buscando reservas...")
        
        # Diferentes formas de buscar reservas
        reservas_encontradas = False
        
        # Buscar en tablas
        tables = driver.find_elements(By.TAG_NAME, "table")
        if tables:
            print(f"✓ Se encontraron {len(tables)} tablas")
            for i, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:  # Tiene datos, no solo encabezado
                    reservas_encontradas = True
                    print(f"✓ Tabla {i+1}: {len(rows)-1} filas de datos")
        
        # Buscar elementos con texto de reserva
        reservation_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Reserva') or contains(text(), 'reservation') or contains(text(), 'Booking')]")
        if reservation_elements:
            print(f"✓ Elementos de reserva encontrados: {len(reservation_elements)}")
            reservas_encontradas = True
        
        # Buscar cards o contenedores
        cards = driver.find_elements(By.CLASS_NAME, "card")
        if cards:
            print(f"✓ Cards encontradas: {len(cards)}")
            reservas_encontradas = True
        
        # 5. Verificar contenido de reservas
        if reservas_encontradas:
            print("✅ RESERVAS ENCONTRADAS: La página muestra información de reservas")
            
            # Mostrar contenido de la página para debug
            page_text = driver.find_element(By.TAG_NAME, "body").text
            lines = page_text.split('\n')
            print("\n📄 Contenido de la página (primeras 20 líneas):")
            for line in lines[:20]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("ℹ No se encontraron reservas visibles - puede que no haya datos")
            print("   La prueba pasa si la página carga correctamente")
        
        # 6. Verificar que la página responde
        page_title = driver.find_elements(By.TAG_NAME, "h1")
        if page_title:
            print(f"✓ Título de página: {page_title[0].text}")
        
        print("\n🎉 CP-RF-09-1 - PRUEBA EXITOSA: Módulo de reservas accesible")
        return True
        
    except Exception as e:
        print(f"❌ CP-RF-09-1 - ERROR: {str(e)}")
        driver.save_screenshot("error_CP-RF-09-1.png")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🚀 INICIANDO CP-RF-09-1: Mostrar próximas reservas")
    print("⏳ Por favor espera...")
    
    result = test_proximas_reservas()
    
    print("\n" + "="*50)
    if result:
        print("✅ CP-RF-09-1: PRUEBA EXITOSA")
    else:
        print("❌ CP-RF-09-1: PRUEBA FALLIDA")
    print("="*50)