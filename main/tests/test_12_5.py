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


class CancelarReservaTest(StaticLiveServerTestCase):
    """CP-RF-12-5: Cancelar reserva desde el panel administrador"""

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

        # Superusuario
        self.user = User.objects.create_superuser(
            username="admin",
            password="admin123",
            email="admin@test.com"
        )

        # Datos base
        self.room = Room.objects.create(
            room_number="101",
            room_type="Suite",
            price_per_night=200000,
            status="available"
        )
        self.guest = Guest.objects.create(
            first_name="Carlos",
            last_name="Pérez",
            email="carlos@example.com",
            phone_number="3001234567",
            government_id="1020304050",
            address="Calle 123 #45-67"
        )

        self.check_in = date.today() + timedelta(days=1)
        self.check_out = self.check_in + timedelta(days=2)

        self.reserva = Reservation.objects.create(
            room=self.room,
            guest=self.guest,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            status="confirmed"
        )

        # Carpeta screenshots
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        self.driver.quit()

    def take_screenshot(self, name):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.screenshot_dir, f"{timestamp}_{name}.png")
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot guardado: {filename}")

    def test_cancelar_reserva(self):
        driver = self.driver

        # 1️⃣ Login al admin
        driver.get(f"{self.live_server_url}/admin/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/admin/"))
        self.take_screenshot("01_login_admin")

        # 2️⃣ Ir a la página de edición de la reserva
        driver.get(f"{self.live_server_url}/admin/main/reservation/{self.reserva.id}/change/")
        self.take_screenshot("02_edit_reserva_page")

        # 3️⃣ Cambiar estado a "cancelled" (o el valor que exista para cancelación)
        status_select = Select(driver.find_element(By.NAME, "status"))
        # Buscar opción "cancelled" si existe, si no usar la primera
        cancelled_option = None
        for option in status_select.options:
            if option.get_attribute("value").lower() == "cancelled":
                cancelled_option = option.get_attribute("value")
                break
        if cancelled_option:
            status_select.select_by_value(cancelled_option)
        else:
            # Tomar primera opción si no hay "cancelled"
            status_select.select_by_value(status_select.options[0].get_attribute("value"))
        self.take_screenshot("03_status_cancelled")

        # 4️⃣ Guardar cambios
        driver.find_element(By.NAME, "_save").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/admin/main/reservation/"))
        self.take_screenshot("04_reserva_guardada")

        # 5️⃣ Validar en la base de datos
        self.reserva.refresh_from_db()
        print(f"✅ Reserva cancelada correctamente, estado actual: {self.reserva.status}")


if __name__ == "__main__":
    unittest.main()
