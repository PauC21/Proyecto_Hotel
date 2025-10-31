#RF-05 Visualizar dashboard 
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, os

User = get_user_model()

class CPRF05Dashboard(TestCase):
    """CP_RF_05: Acceso al dashboard"""

    def setUp(self):
        self.client = Client()
        self.username = 'ana'
        self.password = '1234'
        User.objects.create_user(username=self.username, password=self.password)

    def test_unit_dashboard_con_login(self):
        """Usuario autenticado"""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])

    def test_funcional_dashboard_ui(self):
        """Prueba funcional Selenium"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get("http://127.0.0.1:8000/accounts/login/")

        driver.find_element(By.NAME, "username").send_keys(self.username)
        driver.find_element(By.NAME, "password").send_keys(self.password)
        driver.find_element(By.XPATH, "/html/body/main/form/input[2]").click()
        time.sleep(2)

        os.makedirs("evidencias", exist_ok=True)
        driver.save_screenshot("evidencias/CP_RF_05_dashboard.png")
        driver.quit()
