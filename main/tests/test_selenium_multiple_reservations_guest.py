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
GUEST_DETAIL_URL = f"{BASE_URL}/guests/{7}/"  # Ajustar si la ruta de detalle cambia

USERNAME = "palis"
PASSWORD = "Proyecto2025++"

GUEST_ID = "7"
ROOM_ID = "17"

# Fechas no solapadas
RESERVAS = [
    ("2025-10-22", "2025-10-24"),
    ("2025-10-26", "2025-10-28"),
    ("2025-10-30", "2025-11-02"),
]

SPANISH_MONTHS = {
    "10": "octubre",
    "11": "noviembre",
}

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(driver, name):
    path = os.path.join(SCREENSHOT_DIR, name)
    driver.save_screenshot(path)
    print(f"[CAPTURA] Guardada en: {path}")

def set_date_via_js(driver, element, iso_date):
    driver.execute_script("""
        const el = arguments[0];
        const val = arguments[1];
        el.removeAttribute('min');
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    """, element, iso_date)
    print(f"[DEBUG] Fecha establecida en {element.get_attribute('id')}: {iso_date}")

def scroll_to_reservations_table(driver):
    """
    Desplaza la vista hasta la tabla de reservas del huésped
    para asegurar que quede visible en el screenshot.
    """
    try:
        table = driver.find_element(By.XPATH, "//table[contains(@class,'table') or contains(.,'Reserva')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", table)
        time.sleep(2)  # Esperar que termine el desplazamiento
        print("[DEBUG] Scroll realizado hasta la tabla de reservas.")
    except Exception as e:
        print("[WARN] No se encontró tabla de reservas para hacer scroll:", e)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

def crear_reserva(driver, wait, checkin, checkout, index):
    print(f"[RESERVA {index}] Creando reserva del {checkin} al {checkout}...")
    driver.get(CREATE_URL)
    wait.until(EC.presence_of_element_located((By.ID, "id_guest")))

    Select(driver.find_element(By.ID, "id_guest")).select_by_value(GUEST_ID)
    Select(driver.find_element(By.ID, "id_room")).select_by_value(ROOM_ID)

    checkin_el = driver.find_element(By.ID, "id_check_in_date")
    checkout_el = driver.find_element(By.ID, "id_check_out_date")

    set_date_via_js(driver, checkin_el, checkin)
    set_date_via_js(driver, checkout_el, checkout)

    driver.find_element(By.XPATH, "//button[contains(text(),'Guardar reserva')]").click()
    time.sleep(2)

    html = driver.page_source.lower()
    if "exitosamente" in html or "reserva" in driver.current_url:
        print(f"[RESERVA {index}] ✅ Creada correctamente.")
        return True
    else:
        print(f"[RESERVA {index}] ❌ Falló la creación.")
        return False

def fecha_a_texto(checkin):
    """Convierte '2025-10-22' → '22 de octubre de 2025'"""
    año, mes, dia = checkin.split("-")
    return f"{int(dia)} de {SPANISH_MONTHS[mes]} de {año}"

def main():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        print("[LOGIN] Iniciando sesión...")
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//input[@type='submit' and contains(@value,'Continuar')]").click()
        wait.until(EC.url_contains(BASE_URL))
        print("[LOGIN] Sesión iniciada correctamente.")

        exitosas = 0
        for i, (checkin, checkout) in enumerate(RESERVAS, start=1):
            if crear_reserva(driver, wait, checkin, checkout, i):
                exitosas += 1

        print("[VERIFICACIÓN] Revisando detalle del huésped...")
        driver.get(GUEST_DETAIL_URL)
        time.sleep(4)

        # Hacer scroll hasta la tabla antes del screenshot
        scroll_to_reservations_table(driver)

        page_html = driver.page_source.lower()
        fechas_convertidas = [fecha_a_texto(f[0]).lower() for f in RESERVAS]
        print("[DEBUG] Fechas esperadas en detalle:", fechas_convertidas)

        if exitosas == len(RESERVAS) and all(fc in page_html for fc in fechas_convertidas):
            print("[RESULTADO] ✅ El huésped tiene todas las reservas correctamente asociadas.")
            take_screenshot(driver, "CP-RF-11-1_OK.png")
        else:
            print("[RESULTADO] ❌ No se muestran todas las reservas asociadas correctamente.")
            take_screenshot(driver, "CP-RF-11-1_FAIL.png")

    except Exception as e:
        print("[ERROR]", e)
        take_screenshot(driver, "CP-RF-11-1_ERROR.png")

    finally:
        driver.quit()
        print("=== TEST FINALIZADO ===")

if __name__ == "__main__":
    main()
