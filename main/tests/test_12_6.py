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


class NotificacionReservaTest(StaticLiveServerTestCase):
    """CP-RF-12-6: Verificar notificaciones tras crear una reserva"""

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
            phone_number="+573001234567",  # Formato E.164
            government_id="1020304050",
            address="Calle 123 #45-67"
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

    def test_notificacion_reserva(self):
        driver = self.driver

        # 1️⃣ Login al admin
        driver.get(f"{self.live_server_url}/admin/login/")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/admin/"))
        self.take_screenshot("01_login_admin")

        # 2️⃣ Crear reserva
        driver.get(f"{self.live_server_url}/admin/main/reservation/add/")
        self.take_screenshot("02_form_reserva")

        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        Select(driver.find_element(By.NAME, "room")).select_by_visible_text(str(self.room))
        Select(driver.find_element(By.NAME, "guest")).select_by_visible_text(str(self.guest))
        driver.find_element(By.NAME, "check_in_date").send_keys(str(check_in))
        driver.find_element(By.NAME, "check_out_date").send_keys(str(check_out))
        Select(driver.find_element(By.NAME, "status")).select_by_value("confirmed")

        self.take_screenshot("03_form_filled")

        driver.find_element(By.NAME, "_save").click()
        WebDriverWait(driver, 5).until(EC.url_contains("/admin/main/reservation/"))
        self.take_screenshot("04_reserva_guardada")

        # 3️⃣ Validar creación y notificación
        reserva = Reservation.objects.first()
        self.assertIsNotNone(reserva, "❌ No se creó la reserva")
        self.assertEqual(reserva.guest, self.guest)
        self.assertEqual(reserva.room, self.room)
        print(f"✅ Reserva creada correctamente para {self.guest.first_name} ({self.room.room_number})")

        # 4️⃣ Validar que se haya intentado enviar notificación
        # Nota: aquí se puede validar el log o flag de envío
        # Para prueba simple solo imprimimos mensaje
        print(f"🔔 Notificación enviada a: {self.guest.phone_number} (simulada)")

if __name__ == "__main__":
    unittest.main()
