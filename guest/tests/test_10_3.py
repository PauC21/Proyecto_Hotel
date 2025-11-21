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

class EditarHuespedTest(StaticLiveServerTestCase):
    """CP-RF-10-3: Editar información de un huésped existente"""

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")  # Descomenta si quieres headless
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        # Crear superusuario para login
        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        # Crear huésped inicial
        self.guest = Guest.objects.create(
            first_name="Carlos",
            last_name="Pérez",
            email="carlos.perez@example.com",
            phone_number="3001234567",
            government_id="1020304050",
            address="Calle 123 #45-67"
        )

        # Carpeta de screenshots
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_editar_huesped(self):
        driver = self.driver

        # 1️⃣ Login
        driver.get(f"{self.live_server_url}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continuar']").click()
        time.sleep(1)
        self.take_screenshot("login_edit")

        # 2️⃣ Ir a página de edición del huésped (URL correcta)
        driver.get(f"{self.live_server_url}/guests/{self.guest.id}/update/")

        # Esperar que cargue el input antes de interactuar
        first_name_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "first_name"))
        )
        email_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # 3️⃣ Modificar datos
        first_name_input.clear()
        first_name_input.send_keys("Juan")
        email_input.clear()
        email_input.send_keys("juan.perez@example.com")
        self.take_screenshot("guest_edit_filled")

        # 4️⃣ Enviar formulario
        driver.find_element(
            By.XPATH,
            "//form//button[@type='submit'] | //form//input[@type='submit']"
        ).click()
        time.sleep(1)
        self.take_screenshot("guest_edit_submitted")

        # 5️⃣ Validar cambios en página de detalle
        driver.get(f"{self.live_server_url}/guests/{self.guest.id}/")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Juan", body_text)
        self.assertIn("juan.perez@example.com", body_text)
        print("✅ Prueba exitosa: huésped editado correctamente")

if __name__ == "__main__":
    unittest.main()