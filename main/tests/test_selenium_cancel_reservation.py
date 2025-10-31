import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN GENERAL ---
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
RESERVATION_DETAIL_URL = f"{BASE_URL}/reservation/54"
GUEST_DETAIL_URL = f"{BASE_URL}/guests/6/"

USERNAME = "palis"
PASSWORD = "Proyecto2025++"

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def take_screenshot(driver, name):
    """Guarda una captura de pantalla."""
    path = os.path.join(SCREENSHOT_DIR, name)
    driver.save_screenshot(path)
    print(f"[CAPTURA] Guardada en: {path}")
    return path


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


def main():
    options = Options()
    # options.add_argument("--headless=new")  # Actívalo si no quieres ver el navegador
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # --- LOGIN ---
        print("[LOGIN] Iniciando sesión...")
        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//input[@type='submit' and contains(@value,'Continuar')]").click()
        wait.until(EC.url_contains(BASE_URL))
        print("[LOGIN] Sesión iniciada correctamente.")

        # --- ABRIR DETALLE DE LA RESERVA ---
        print("[RESERVA] Accediendo al detalle de la reserva #54...")
        driver.get(RESERVATION_DETAIL_URL)
        time.sleep(3)  # Espera base para que cargue contenido

        # Esperar algún elemento clave de la página
        try:
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Reserva') or contains(., 'Detalle')]"))
            )
            print("[RESERVA] Página cargada correctamente.")
        except:
            print("[ADVERTENCIA] No se detectó título de 'Detalle de la Reserva', intentando continuar.")

        # --- BUSCAR Y CLICKEAR EL BOTÓN ---
        print("[ACCION] Buscando botón de cancelar reserva...")
        cancel_button = None
        xpath_posibles = [
            "//button[contains(., 'Cancelar') or contains(., '❌')]",
            "//input[contains(@value, 'Cancelar')]",
            "//a[contains(., 'Cancelar')]",
        ]

        for xpath in xpath_posibles:
            try:
                cancel_button = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                print(f"[ENCONTRADO] Botón localizado con selector: {xpath}")
                break
            except:
                continue

        if not cancel_button:
            print("[ERROR] ❌ No se encontró el botón de cancelar reserva en la página.")
            raise Exception("Botón de cancelar no encontrado")

        # Scroll hasta el botón para asegurar clic
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cancel_button)
        time.sleep(1)

        print("[ACCION] Haciendo clic en el botón de cancelar...")
        cancel_button.click()

        # Confirmar alerta si aparece
        try:
            alert = wait.until(EC.alert_is_present())
            print("[CONFIRMACIÓN] Se mostró alerta de confirmación.")
            alert.accept()
        except:
            print("[CONFIRMACIÓN] No se detectó alerta.")

        # Esperar posible redirección
        time.sleep(3)
        page_html = driver.page_source.lower()
        if "cancelada" in page_html or "cancelado" in page_html:
            print("[RESULTADO] ✅ Reserva marcada como cancelada correctamente.")
        else:
            print("[RESULTADO] ⚠️ No se detectó texto de cancelación en la página.")

        # --- VALIDAR EN DETALLE DE HUÉSPED ---
        print("[VERIFICACIÓN] Abriendo detalle del huésped 6...")
        driver.get(GUEST_DETAIL_URL)
        time.sleep(3)

        try:
            table = driver.find_element(By.XPATH, "//table[contains(.,'Reserva')]")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", table)
        except:
            scroll_to_bottom(driver)

        guest_html = driver.page_source.lower()
        if "#54" in guest_html and "cancelada" in guest_html:
            print("[VALIDACIÓN FINAL] ✅ Reserva #54 aparece como cancelada.")
            take_screenshot(driver, "CP-RF-11-2_OK.png")
        else:
            print("[VALIDACIÓN FINAL] ❌ No se visualiza correctamente la reserva cancelada.")
            take_screenshot(driver, "CP-RF-11-2_FAIL.png")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        take_screenshot(driver, "CP-RF-11-2_ERROR.png")

    finally:
        driver.quit()
        print("=== TEST FINALIZADO ===")


if __name__ == "__main__":
    main()
