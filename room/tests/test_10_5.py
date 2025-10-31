import time
import unittest
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
import chromedriver_autoinstaller
from guest.models import Guest  # Importamos solo Guest

chromedriver_autoinstaller.install()

class CrearHuespedDuplicadoTest(StaticLiveServerTestCase):
    """CP-RF-10-5: Crear huésped con documento duplicado"""

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Crear huésped inicial para duplicar
        Guest.objects.create(
            first_name="Carlos",
            last_name="Pérez",
            email="carlos.perez@example.com",
            phone_number="3001234567",
            government_id="1020304050",
            address="Calle 123 #45-67"
        )

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_crear_huesped_duplicado(self):
        driver = self.driver

        # Login
        driver.get(f"{self.live_server_url}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continuar']").click()
        time.sleep(1)
        self.take_screenshot("login")

        # Ir a creación de huésped
        driver.get(f"{self.live_server_url}/guests/create/")
        driver.find_element(By.NAME, "first_name").send_keys("Juan")
        driver.find_element(By.NAME, "last_name").send_keys("Gómez")
        driver.find_element(By.NAME, "email").send_keys("juan.gomez@example.com")
        driver.find_element(By.NAME, "phone_number").send_keys("3007654321")
        driver.find_element(By.NAME, "government_id").send_keys("1020304050")  # Duplicado
        driver.find_element(By.NAME, "address").send_keys("Calle 456 #78-90")
        self.take_screenshot("guest_filled_duplicate")

        # Enviar formulario
        driver.find_element(
            By.XPATH,
            "//form//button[@type='submit'] | //form//input[@type='submit']"
        ).click()
        time.sleep(1)
        self.take_screenshot("guest_submit_duplicate")

        # Validar mensaje de error por documento duplicado
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("ya existe", body_text.lower())
        print("✅ Prueba exitosa: validación de documento duplicado")