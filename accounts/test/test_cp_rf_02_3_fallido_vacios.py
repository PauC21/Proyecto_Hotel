from django.test import TestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF02_3_Vacios(TestCase):
    """CP-RF-02-3: Actualizar perfil con campos vacíos"""

    def setUp(self):
        self.user = User.objects.create_user(username="palis", password="temporal123", email="palis@hotel.com")

    def test_funcional_perfil_vacios(self):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("http://127.0.0.1:8000/accounts/login/")

        # Login
        driver.find_element(By.NAME, "username").send_keys("palis")
        driver.find_element(By.NAME, "password").send_keys("Proyecto2025++")
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Ir a perfil
        driver.get("http://127.0.0.1:8000/accounts/profile/")
        time.sleep(1)

        # Vaciar campos
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()

        # Guardar
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Captura
        os.makedirs("evidencias/CP-RF-02", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-02/CP-RF-02-3_fallido_vacios.png")

        # Validar mensaje del navegador (HTML5)
        validation_msg = email_input.get_attribute("validationMessage")
        self.assertTrue(
            "Completa este campo" in validation_msg or "Please fill in this field" in validation_msg
        )

        driver.quit()
