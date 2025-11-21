import time
import unittest
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

class CrearHuespedValidoTest(StaticLiveServerTestCase):
    """Prueba funcional con Selenium: crear huésped válido (con screenshots)"""

    def setUp(self):
        chrome_options = Options()
        # Quita el modo headless si quieres ver el navegador:
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        # Crear carpeta de screenshots si no existe
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        """Guarda una captura de pantalla con el nombre dado"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_crear_huesped_valido(self):
        driver = self.driver

        # 1️⃣ Ir a página de login
        driver.get(f"{self.live_server_url}/accounts/login/")
        time.sleep(1)
        self.take_screenshot("01_login_page")

        # 2️⃣ Iniciar sesión
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        # Clic en el botón de login (input submit value="Continuar")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continuar']").click()
        time.sleep(2)
        self.take_screenshot("02_logged_in")

        # Verificamos que la URL cambió (opcional)
        print("URL actual:", driver.current_url)

        # 3️⃣ Ir a la página de creación de huésped
        driver.get(f"{self.live_server_url}/guests/create/")
        time.sleep(2)
        self.take_screenshot("03_guest_form")

        # 4️⃣ Llenar el formulario de huésped
        driver.find_element(By.NAME, "first_name").send_keys("Carlos")
        driver.find_element(By.NAME, "last_name").send_keys("Pérez")
        driver.find_element(By.NAME, "email").send_keys("carlos.perez@example.com")
        driver.find_element(By.NAME, "phone_number").send_keys("3001234567")
        driver.find_element(By.NAME, "government_id").send_keys("1020304050")
        driver.find_element(By.NAME, "address").send_keys("Calle 123 #45-67")
        self.take_screenshot("04_guest_filled")

        # 5️⃣ Enviar el formulario (acepta button o input submit)
        driver.find_element(
            By.XPATH,
            "//form//button[@type='submit'] | //form//input[@type='submit']"
        ).click()
        time.sleep(2)
        self.take_screenshot("05_guest_created")

        # 6️⃣ Validar que aparece la información del huésped en la página de detalle
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Carlos", body_text)
        self.assertIn("Pérez", body_text)
        self.assertIn("1020304050", body_text)

        print("✅ Prueba exitosa: huésped creado correctamente")


if __name__ == "__main__":
    unittest.main()