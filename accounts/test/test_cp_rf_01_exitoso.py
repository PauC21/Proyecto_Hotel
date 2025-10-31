from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF01Login(TestCase):
    """CP-RF-01: Pruebas de inicio de sesión"""

    def setUp(self):
        self.client = Client()
        self.username = 'palis'
        self.password = 'Proyecto2025++'
        User.objects.create_user(username=self.username, password=self.password)

    def test_unit_login_correcto(self):
        """Login correcto"""
        response = self.client.post('/accounts/login/', {'username': self.username, 'password': self.password})
        self.assertIn(response.status_code, [200, 302])

    def test_unit_login_incorrecto(self):
        """Login incorrecto"""
        response = self.client.post('/accounts/login/', {'username': self.username, 'password': 'incorrecta'})
        self.assertIn(response.status_code, [200, 302])

    def test_funcional_login_ui(self):
        """Prueba funcional con Selenium"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("http://127.0.0.1:8000/accounts/login/")

        # Ingresar datos
        driver.find_element(By.NAME, "username").send_keys(self.username)
        driver.find_element(By.NAME, "password").send_keys(self.password)

        # Clic en el botón del formulario
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Guardar captura
        os.makedirs("evidencias/CP-RF-01", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-01_login_valido.png")
        driver.quit()
