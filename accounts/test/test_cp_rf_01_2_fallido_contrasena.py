from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

class CPRF01_2_LoginIncorrecto(TestCase):
    """CP-RF-01-2: Login con contraseña incorrecta"""

    def test_funcional_login_contrasena_incorrecta(self):
        """Verifica mensaje de error con contraseña incorrecta"""

        # Inicializar Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Abrir página de login
        driver.get("http://127.0.0.1:8000/accounts/login/")
        time.sleep(1)

        # Ingresar usuario y contraseña incorrecta
        driver.find_element(By.NAME, "username").send_keys("palis")
        driver.find_element(By.NAME, "password").send_keys("Proyecto2025++")

        # Clic en el botón del formulario
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Buscar mensaje de error esperado
        page_source = driver.page_source
        expected_msg = "Por favor, introduzca un nombre de usuario y clave correctos."

        # Crear carpeta de evidencias
        os.makedirs("evidencias/CP-RF-01", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-01/CP-RF-01-2_fallido_contrasena.png")

        # Validar
        self.assertIn(expected_msg, page_source)

        driver.quit()
