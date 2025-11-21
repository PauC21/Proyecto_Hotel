import time
import os
import unittest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
import chromedriver_autoinstaller
from guest.models import Guest  # Ajusta si tu modelo se llama diferente

chromedriver_autoinstaller.install()

class EliminarHuespedSinReservasTest(StaticLiveServerTestCase):
    """CP-RF-10-4: Eliminar huésped que no tiene reservas"""

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        # Crear superusuario
        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        # Crear huésped sin reservas
        self.guest = Guest.objects.create(
            first_name="Carlos",
            last_name="Pérez",
            email="carlos.perez@example.com",
            phone_number="3001234567",
            government_id="1020304050",
            address="Calle 123 #45-67"
        )

        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_eliminar_huesped_sin_reservas(self):
        driver = self.driver

        # Login
        driver.get(f"{self.live_server_url}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continuar']").click()
        time.sleep(1)
        self.take_screenshot("login_delete")

        # Ir a página de eliminación
        driver.get(f"{self.live_server_url}/guests/{self.guest.id}/delete/")

        # Esperar que el botón de eliminar esté presente
        delete_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//form//button[@type='submit'] | //form//input[@type='submit']"))
        )
        delete_button.click()
        time.sleep(1)
        self.take_screenshot("guest_deleted")

        # Validar que el huésped ya no exista
        driver.get(f"{self.live_server_url}/guests/{self.guest.id}/")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("No encontrado", body_text)  # Ajusta según tu mensaje real
        print("✅ Prueba exitosa: huésped eliminado sin reservas")
