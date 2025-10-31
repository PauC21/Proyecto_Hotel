import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class LogoutTest(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.get("http://127.0.0.1:8000/login/")  # Asegúrate de que esta ruta sea correcta

    def test_cerrar_sesion(self):
        driver = self.driver

        # 1️⃣ Iniciar sesión
        driver.find_element(By.NAME, "username").send_keys("palis")  # Cambia por tu usuario válido
        driver.find_element(By.NAME, "password").send_keys("Proyecto2025++")  # Cambia por tu contraseña válida
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        # 2️⃣ Verificar que haya iniciado correctamente (por ejemplo, panel principal visible)
        self.assertIn("dashboard", driver.current_url.lower())

        # 3️⃣ Hacer clic en “Cerrar sesión”
        logout_link = driver.find_element(By.LINK_TEXT, "Cerrar sesión")
        logout_link.click()
        time.sleep(2)

        # 4️⃣ Comprobar redirección al login
        self.assertIn("login", driver.current_url.lower())

        # 5️⃣ Intentar volver atrás (no debe acceder)
        driver.back()
        time.sleep(1)
        self.assertIn("login", driver.current_url.lower())

        # Captura de pantalla
        driver.save_screenshot("screenshots/test_logout.png")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
