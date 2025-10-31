from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

class CPRF01_3_LoginVacio(TestCase):
    """CP-RF-01-3: Login con campos vacíos"""

    def test_funcional_login_campos_vacios(self):
        """Verifica validación con campos vacíos"""

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Abrir formulario
        driver.get("http://127.0.0.1:8000/accounts/login/")
        time.sleep(1)

        # No llenar los campos
        # Clic en el botón “continuar”
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Capturar evidencia
        os.makedirs("evidencias/CP-RF-01", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-01/CP-RF-01-3_fallido_vacios.png")

        # Validar mensaje del navegador
        username_input = driver.find_element(By.NAME, "username")
        validation_msg = username_input.get_attribute("validationMessage")

        # Mensaje esperado
        expected_msg = "Completa este campo"

        self.assertTrue("Completa este campo" in validation_msg or "Please fill in this field" in validation_msg)

        driver.quit()
