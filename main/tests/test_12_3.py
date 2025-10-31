import time
import os
import unittest
from datetime import date, timedelta
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
import chromedriver_autoinstaller

from guest.models import Guest
from room.models import Room
from main.models import Reservation

chromedriver_autoinstaller.install()


class CrearReservaFechasInvalidasTest(StaticLiveServerTestCase):
    """CP-RF-12-3: Intentar crear reserva con fechas inválidas (check-out antes de check-in)"""

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")  # descomentar si no quieres ver navegador
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        # Crear superusuario
        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        # Crear habitación disponible
        self.room = Room.objects.create(
            room_number="103",
            room_type="Suite",
            price_per_night=200000,
            status="available"
        )

        # Crear huésped
        self.guest = Guest.objects.create(
            first_name="Luis",
            last_name="Martínez",
            email="luis@example.com",
            phone_number="3009876543",
            government_id="5566778899",
            address="Calle 456 #12-34"
        )

        # Carpeta para screenshots
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_reserva_fechas_invalidas(self):
        driver = self.driver

        # 1️⃣ Login al admin
        driver.get(f"{self.live_server_url}/admin/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/admin/"))
        self.take_screenshot("01_login_admin")

        # 2️⃣ Ir a crear reserva
        driver.get(f"{self.live_server_url}/admin/main/reservation/add/")
        self.take_screenshot("02_form_reserva")

        # 3️⃣ Llenar formulario con fechas inválidas (check-out < check-in)
        Select(driver.find_element(By.NAME, "room")).select_by_visible_text(str(self.room))
        Select(driver.find_element(By.NAME, "guest")).select_by_visible_text(str(self.guest))

        check_in = date.today() + timedelta(days=5)
        check_out = date.today() + timedelta(days=3)  # ❌ check-out antes que check-in

        driver.find_element(By.NAME, "check_in_date").send_keys(str(check_in))
        driver.find_element(By.NAME, "check_out_date").send_keys(str(check_out))
        Select(driver.find_element(By.NAME, "status")).select_by_value("confirmed")
        self.take_screenshot("03_form_filled_invalid_dates")

        # 4️⃣ Intentar guardar
        driver.find_element(By.NAME, "_save").click()
        self.take_screenshot("04_intento_guardar_invalid_dates")

        # 5️⃣ Validar que no se creó la reserva
        reservas = Reservation.objects.filter(room=self.room)
        self.assertEqual(reservas.count(), 0, "❌ La reserva no debería haberse creado")
        print("✅ La reserva no se creó porque las fechas eran inválidas")


if __name__ == "__main__":
    unittest.main()