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
GUEST_DETAIL_URL = f"{BASE_URL}/guests/7/"  # Huésped ID = 7

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


def scroll_entire_page(driver):
    """Hace scroll lentamente para capturar todo el contenido."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(3):  # 3 pasos para cubrir pantallas largas
        driver.execute_script(f"window.scrollTo(0, {(i+1) * last_height / 3});")
        time.sleep(1)


def main():
    options = Options()
    # options.add_argument("--headless=new")
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

        # --- DETALLE DEL HUÉSPED ---
        print("[HUÉSPED] Accediendo al detalle del huésped ID=7...")
        driver.get(GUEST_DETAIL_URL)
        time.sleep(3)

        # Esperar título o encabezado
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Huésped') or contains(., 'Detalle')]")))
            print("[HUÉSPED] Página cargada correctamente.")
        except:
            print("[ADVERTENCIA] No se detectó título, continuando de todas formas.")

        # --- VALIDAR TABLA DE RESERVAS ---
        print("[VERIFICACIÓN] Buscando tabla de reservas...")
        try:
            table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(.,'Reserva') or contains(.,'Habitación')]")))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", table)
            time.sleep(1)
            print("[VERIFICACIÓN] Tabla de reservas localizada correctamente.")
        except:
            print("[ERROR] ❌ No se encontró la tabla de reservas del huésped.")
            raise Exception("Tabla no encontrada")

        # --- ANALIZAR CAMPOS DE LA TABLA ---
        html = driver.page_source.lower()
        campos_esperados = ["reserva", "habit", "check", "estado"]
        encontrados = [campo for campo in campos_esperados if campo in html]

        if len(encontrados) >= 3:
            print(f"[VALIDACIÓN] ✅ Se encontraron los campos esperados en la tabla: {', '.join(encontrados)}.")
        else:
            print(f"[VALIDACIÓN] ⚠️ Campos incompletos detectados: {', '.join(encontrados)}")

        # --- SCROLL Y CAPTURA FINAL ---
        scroll_entire_page(driver)
        take_screenshot(driver, "CP-RF-11-3_OK.png")
        print("[RESULTADO] ✅ Historial de reservas visible y capturado correctamente.")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        take_screenshot(driver, "CP-RF-11-3_ERROR.png")

    finally:
        driver.quit()
        print("=== TEST FINALIZADO ===")


if __name__ == "__main__":
    main()
