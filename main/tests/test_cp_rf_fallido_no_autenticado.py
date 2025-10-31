from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF05_2_DashboardSinSesion(TestCase):
    """CP_RF_05_2: Intento de acceder al dashboard sin sesión"""

    def setUp(self):
        self.client = Client()
        # Creamos usuario válido
        self.username = "ana"
        self.password = "1234"
        User.objects.create_user(username=self.username, password=self.password)

    def test_unit_dashboard_sin_login(self):
        """Verifica redirección al intentar acceder sin autenticarse"""
        # Usuario no autenticado intenta acceder
        response = self.client.get("/dashboard/", follow=True)
        redirect_url = response.redirect_chain[-1][0] if response.redirect_chain else ""
        self.assertTrue(
            "/login" in redirect_url or "/accounts/login" in redirect_url,
            f"No se redirigió al login. URL obtenida: {redirect_url}"
        )

    def test_funcional_dashboard_ui_sin_login(self):
        """Prueba funcional Selenium: acceso al dashboard con contraseña incorrecta"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        # Ir a login
        driver.get("http://127.0.0.1:8000/accounts/login/")
        time.sleep(2)

        # Ingresar usuario correcto, pero contraseña incorrecta
        driver.find_element(By.XPATH, "//*[@id='id_username']").send_keys("ana")
        driver.find_element(By.XPATH, "//*[@id='id_password']").send_keys("clave_incorrecta")
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        # Intentar acceder manualmente al dashboard
        driver.get("http://127.0.0.1:8000/dashboard/")
        time.sleep(2)

        
        # Guardar evidencia
        os.makedirs("evidencias", exist_ok=True)
        driver.save_screenshot("evidencias/CP_RF_05_fallido_no_autenticado.png")
        driver.quit()
