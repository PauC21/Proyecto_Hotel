from django.test import TestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF02_2_CorreoInvalido(TestCase):
    """CP-RF-02-2: Actualizar perfil con correo inválido"""

    def setUp(self):
        self.user = User.objects.create_user(username="palis", password="Proyecto2025++", email="paulaa-cuellarr@unilibre.edu.co")

    def test_funcional_correo_invalido(self):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("http://127.0.0.1:8000/accounts/login/")

        # Login
        driver.find_element(By.NAME, "username").send_keys("palis")
        driver.find_element(By.NAME, "password").send_keys("temporal123")
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Ir al perfil
        driver.get("http://127.0.0.1:8000/accounts/profile/")
        time.sleep(1)

        # Correo inválido
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys("usuario@.com")

        # Guardar
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Captura
        os.makedirs("evidencias/CP-RF-02", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-02/CP-RF-02-2_fallido_correo_invalido.png")

        # Validación de error (por mensaje del navegador)
        validation_msg = email_input.get_attribute("validationMessage")
        self.assertTrue(
            "Please include an" in validation_msg or "incluye un" in validation_msg
        )

        driver.quit()