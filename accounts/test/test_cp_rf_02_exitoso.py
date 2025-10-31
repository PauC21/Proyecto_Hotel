from django.test import TestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF02_1_PerfilValido(TestCase):
    """CP-RF-02-1: Actualizar perfil con datos válidos"""

    def setUp(self):
        self.user = User.objects.create_user(username="palis", password="Proyecto2025++", email="paulaa-cuellarr@unilibre.edu.co")

    def test_funcional_actualizar_perfil_valido(self):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("http://127.0.0.1:8000/accounts/login/")

        # Login
        driver.find_element(By.NAME, "username").send_keys("palis")
        driver.find_element(By.NAME, "password").send_keys("Proyecto2025++")
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Ir al perfil (ajusta la URL según tu sistema si difiere)
        driver.get("http://127.0.0.1:8000/accounts/profile/")
        time.sleep(1)

        # Llenar campos válidos
        driver.find_element(By.NAME, "email").clear()
        driver.find_element(By.NAME, "email").send_keys("nuevo@correo.com")

        # Clic en guardar cambios (ajusta el XPath si difiere)
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Captura de evidencia
        os.makedirs("evidencias/CP-RF-02", exist_ok=True)
        driver.save_screenshot("evidencias/CP-RF-02/CP-RF-02-1_exitoso.png")

        # Verificación
        self.assertIn("nuevo@correo.com", driver.page_source)
        driver.quit()
