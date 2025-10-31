# CP-RF-13-1: Registrar Check-In exitoso (con diagnóstico extendido)
from django.test import TestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

User = get_user_model()

class CPRF13_1_CheckInExitoso(TestCase):
    """Caso de Prueba RF-13-1: Registrar Check-In exitoso"""

    def setUp(self):
        self.username = "ana"
        self.password = "1234"
        User.objects.create_user(username=self.username, password=self.password)

    def test_funcional_checkin_exitoso(self):
        """Prueba funcional: registrar un check-in correctamente"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        wait = WebDriverWait(driver, 15)
        driver.maximize_window()

        try:
            # --- Ingresar al login ---
            driver.get("http://127.0.0.1:8000/accounts/login/")
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_username"]')))
            driver.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(self.username)
            driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(self.password)
            driver.find_element(By.XPATH, '/html/body/main/form/input[2]').click()

            # --- Ir a "Crear reservación" ---
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/nav/ul/li[8]/a')))
            driver.find_element(By.XPATH, '/html/body/nav/ul/li[8]/a').click()

            # --- Esperar que cargue el formulario ---
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_guest"]')))

            # --- Seleccionar Guest (Paula Cuellar) ---
            guest_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="id_guest"]'))
            guest_dropdown.select_by_visible_text("Paula Cuellar (1014176160)")

            # --- Seleccionar Room (Habitación 1) ---
            room_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="id_room"]'))
            room_dropdown.select_by_visible_text("Habitación 1 (Disponible)")

            # --- Usar fechas fijas ---
            checkin_field = driver.find_element(By.XPATH, '//*[@id="id_check_in_date"]')
            checkout_field = driver.find_element(By.XPATH, '//*[@id="id_check_out_date"]')

            # Limpia el campo por si tiene valor predefinido
            driver.execute_script("arguments[0].value = '';", checkin_field)
            driver.execute_script("arguments[0].value = '';", checkout_field)

            # Establece la fecha directamente con JavaScript (más confiable que send_keys)
            driver.execute_script("arguments[0].value = '2025-10-30';", checkin_field)
            driver.execute_script("arguments[0].value = '2025-10-31';", checkout_field)


            # --- Cambiar estado a "Confirmada" ---
            status_dropdown = Select(driver.find_element(By.XPATH, '//*[@id="id_status"]'))
            status_dropdown.select_by_visible_text("Confirmada")

            # --- Captura antes de guardar ---
            os.makedirs("evidencias", exist_ok=True)
            driver.save_screenshot("evidencias/CP-RF-13-1_antes_guardar.png")

            # --- Guardar reserva ---
            driver.find_element(By.XPATH, '/html/body/main/form/button').click()

            # --- Intentar esperar redirección ---
            try:
                wait.until(EC.url_contains("reservations"))
            except:
                # Guardamos pantallazo y mostramos HTML para diagnóstico
                driver.save_screenshot("evidencias/CP-RF-13-1_error_guardar.png")
                html = driver.page_source
                print("\n[⚠️ DEBUG] El formulario no redirigió correctamente.\n")
                print("Primeros 1500 caracteres del HTML:\n")
                print(html[:1500])  # imprime en consola para ver el motivo
                raise AssertionError("No se redirigió correctamente tras guardar la reserva.")

            # --- Validar redirección correcta ---
            current_url = driver.current_url
            self.assertIn("reservations", current_url, f"URL inesperada: {current_url}")

            # --- Captura final ---
            driver.save_screenshot("evidencias/CP-RF-13-1_checkin_exitoso.png")

        finally:
            driver.quit()
