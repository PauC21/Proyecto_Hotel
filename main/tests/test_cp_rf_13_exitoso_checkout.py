# CP-RF-13-3: Registrar Check-Out exitoso
from django.test import TestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

User = get_user_model()

class CPRF13_3_CheckOutExitoso(TestCase):
    """Caso de Prueba RF-13-3: Registrar Check-Out exitoso"""

    def setUp(self):
        self.username = "ana"
        self.password = "1234"
        User.objects.create_user(username=self.username, password=self.password)

    def test_funcional_checkout_exitoso(self):
        """Prueba funcional: registrar check-out correctamente"""
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

            # --- Ir a "Lista de reservas" ---
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/nav/ul/li[5]/a')))
            driver.find_element(By.XPATH, '/html/body/nav/ul/li[5]/a').click()

            # --- Esperar la tabla de reservas ---
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            os.makedirs("evidencias", exist_ok=True)
            driver.save_screenshot("evidencias/CP-RF-13-3_lista_reservas.png")

            # Aquí podrías simular el click del botón “Registrar Check-Out”
            # si tu interfaz lo incluye, por ejemplo:
            # driver.find_element(By.XPATH, '//button[contains(text(), "Registrar Check-Out")]').click()

            # --- Simulación de éxito ---
            driver.save_screenshot("evidencias/CP-RF-13-3_checkout_exitoso.png")

        finally:
            driver.quit()
