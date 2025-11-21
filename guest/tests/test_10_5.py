import time
import os
from datetime import date
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
import chromedriver_autoinstaller

from guest.models import Guest
from main.models import Reservation
from room.models import Room

chromedriver_autoinstaller.install()


class EliminarHuespedConReservasTest(StaticLiveServerTestCase):
    """CP-RF-10-5: Intentar eliminar huésped con reservas activas"""

    def setUp(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
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

        # Crear huésped con reserva
        self.guest = Guest.objects.create(
            first_name="Juliana",
            last_name="Gomez",
            email="juliana@example.com",
            phone_number="3220000000",
            government_id="1090456789",
            address="Mi casa"
        )

        # Crear habitación y reserva activa
        self.room = Room.objects.create(
            room_number="101",
            room_type="Sencilla",
            price_per_night=150000,
            status="available"
        )

        self.reserva = Reservation.objects.create(
            guest=self.guest,
            room=self.room,
            check_in_date=date(2025, 11, 21),
            check_out_date=date(2025, 11, 22),
            status="confirmed"
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

    def test_eliminar_huesped_con_reservas(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        # 1️⃣ Login
        driver.get(f"{self.live_server_url}/accounts/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Continuar']").click()
        time.sleep(1)
        self.take_screenshot("login_huesped")

        # 2️⃣ Ir a página de eliminación del huésped
        driver.get(f"{self.live_server_url}/guests/{self.guest.id}/delete/")
        time.sleep(1)
        self.take_screenshot("pagina_eliminar_huesped")

        # 3️⃣ Intentar eliminar
        delete_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//form//button[@type='submit'] | //form//input[@type='submit']"))
        )
        delete_button.click()
        time.sleep(1)
        self.take_screenshot("intento_eliminar_huesped")

        # 4️⃣ Validar que NO se eliminó y que aparece mensaje de error
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("No se puede eliminar el huésped porque tiene reservas activas", body_text)
        print("✅ Prueba exitosa: huésped con reservas activas no fue eliminado")