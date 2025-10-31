import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuración general ---
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
CREATE_URL = f"{BASE_URL}/reservation/create/"

USERNAME = "palis"
PASSWORD = "Proyecto2025++"

CHECKIN = "2025-10-22"
CHECKOUT = "2025-10-24"
GUEST_ID = "6"
ROOM_ID = "16"

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(driver, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    driver.save_screenshot(path)
    print(f"[CAPTURA] Guardada en: {path}")

# --- Función auxiliar para establecer fechas correctamente ---
def set_date_via_js(driver, element, iso_date):
    """Asigna un valor ISO (YYYY-MM-DD) a un input type=date usando JS."""
    driver.execute_script("""
        const el = arguments[0];
        const val = arguments[1];
        el.removeAttribute('min'); // por si el min bloquea
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    """, element, iso_date)
    print(f"[DEBUG] Fecha establecida en {element.get_attribute('id')}: {iso_date}")

def main():
    options = Options()
    # Si quieres ver el navegador, deja visible:
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print("[LOGIN] Cargando página de login...")
        driver.get(LOGIN_URL)

        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//input[@type='submit' and contains(@value,'Continuar')]").click()

        wait.until(EC.url_contains(BASE_URL))
        print("[LOGIN] Sesión iniciada correctamente")

        # Ir a crear reserva
        print("[RESERVA] Abriendo formulario de creación...")
        driver.get(CREATE_URL)
        wait.until(EC.presence_of_element_located((By.ID, "id_guest")))

        print("[RESERVA] Llenando formulario...")

        # seleccionar huésped
        Select(driver.find_element(By.ID, "id_guest")).select_by_value(GUEST_ID)

        # seleccionar habitación
        Select(driver.find_element(By.ID, "id_room")).select_by_value(ROOM_ID)

        # --- NUEVA FORMA DE ESTABLECER FECHAS ---
        checkin_el = driver.find_element(By.ID, "id_check_in_date")
        checkout_el = driver.find_element(By.ID, "id_check_out_date")

        set_date_via_js(driver, checkin_el, CHECKIN)
        set_date_via_js(driver, checkout_el, CHECKOUT)

        # Verificar que se asignaron bien
        print("[DEBUG] Check-in:", checkin_el.get_attribute("value"))
        print("[DEBUG] Check-out:", checkout_el.get_attribute("value"))

        # Enviar formulario
        print("[RESERVA] Enviando formulario...")
        driver.find_element(By.XPATH, "//button[contains(text(),'Guardar reserva')]").click()

        time.sleep(2)
        page_html = driver.page_source.lower()

        if "exitosamente" in page_html or "reserva" in driver.current_url:
            print("[RESULTADO] ✅ Reserva creada exitosamente.")
            take_screenshot(driver, "CP-RF-14-1_OK.png")
        else:
            print("[RESULTADO] ❌ No se detectó mensaje de éxito ni redirección.")
            take_screenshot(driver, "CP-RF-14-1_FAIL.png")

    except Exception as e:
        print("[ERROR]", e)
        take_screenshot(driver, "CP-RF-14-1_ERROR.png")

    finally:
        driver.quit()
        print("=== TEST FINALIZADO ===")

if __name__ == "__main__":
    main()
