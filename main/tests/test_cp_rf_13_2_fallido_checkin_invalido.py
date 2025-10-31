# CP-RF-13-2: Registrar Check-In en reserva cancelada o finalizada
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

class CPRF13_2_CheckInInvalido(TestCase):
    """Caso de Prueba RF-13-2: Intentar registrar Check-In en reserva cancelada o finalizada"""

    def setUp(self):
        self.username = "ana"
        self.password = "1234"
        User.objects.create_user(username=self.username, password=self.password)

    def test_funcional_checkin_invalido(self):
        """Prueba funcional: no debe permitir check-in en reserva cancelada/finalizada"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        wait = WebDriverWait(driver, 15)
        driver.maximize_window()

        try:
            # --- Iniciar sesión ---
            driver.get("http://127.0.0.1:8000/accounts/login/")
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_username"]')))
            driver.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(self.username)
            driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(self.password)
            driver.find_element(By.XPATH, '/html/body/main/form/input[2]').click()

            # --- Ir a "Crear reservación" ---
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/nav/ul/li[8]/a')))
            driver.find_element(By.XPATH, '/html/body/nav/ul/li[8]/a').click()

            # --- Esperar formulario ---
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id_guest"]')))

            # --- Seleccionar Guest ---
            Select(driver.find_element(By.XPATH, '//*[@id="id_guest"]')).select_by_visible_text("Paula Cuellar (1014176160)")

            # --- Seleccionar Room ---
            Select(driver.find_element(By.XPATH, '//*[@id="id_room"]')).select_by_visible_text("Habitación 1 (Disponible)")

            # --- Establecer fechas fijas ---
            driver.execute_script("arguments[0].value='2025-10-30';", driver.find_element(By.XPATH, '//*[@id="id_check_in_date"]'))
            driver.execute_script("arguments[0].value='2025-10-31';", driver.find_element(By.XPATH, '//*[@id="id_check_out_date"]'))

            # --- Cambiar estado a "Cancelada" ---
            Select(driver.find_element(By.XPATH, '//*[@id="id_status"]')).select_by_visible_text("Cancelada")

            os.makedirs("evidencias", exist_ok=True)
            driver.save_screenshot("evidencias/CP-RF-13-2_cancelada_antes_guardar.png")

            # --- Guardar reserva ---
            driver.find_element(By.XPATH, '/html/body/main/form/button').click()

            # --- Validar que no cambió la página ---
            current_url = driver.current_url
            self.assertIn("reservation/create", current_url, "El sistema no debería permitir guardar una reserva cancelada.")

            driver.save_screenshot("evidencias/CP-RF-13-2_error_guardar.png")

        finally:
            driver.quit()
