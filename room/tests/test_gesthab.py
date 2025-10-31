import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class TestGestionHabitaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuración inicial del navegador y login"""
        options = Options()
        options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.wait = WebDriverWait(cls.driver, 10)

        # Crear carpeta de capturas
        cls.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(cls.screenshot_dir, exist_ok=True)

        cls.driver.get("http://127.0.0.1:8000/")
        time.sleep(2)
        cls.login_admin()

    @classmethod
    def login_admin(cls):
        """Inicio de sesión como administrador"""
        driver = cls.driver
        driver.get("http://127.0.0.1:8000/login/")
        try:
            username = cls.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password = driver.find_element(By.NAME, "password")

            username.send_keys("admin")
            password.send_keys("admin123")  # cambia si tu clave es diferente
            driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

            cls.wait.until(EC.url_contains("/dashboard"))
            cls.save_screenshot("login_admin_ok.png")
        except Exception as e:
            cls.save_screenshot("login_admin_fail.png")
            raise e

    @classmethod
    def save_screenshot(cls, name):
        """Guardar capturas de pantalla en la carpeta definida"""
        path = os.path.join(cls.screenshot_dir, name)
        cls.driver.save_screenshot(path)

    # ----------------------------------------------------------
    # 🔹 Caso 1: Crear habitación válida
    # ----------------------------------------------------------
    def test_crear_habitacion_valida(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/rooms/add/")
        try:
            numero = self.wait.until(EC.presence_of_element_located((By.NAME, "room_number")))
            tipo = driver.find_element(By.NAME, "room_type")
            precio = driver.find_element(By.NAME, "price")
            estado = driver.find_element(By.NAME, "status")

            numero.send_keys("101")
            tipo.send_keys("Suite")
            precio.send_keys("250000")
            estado.send_keys("Disponible")

            driver.find_element(By.XPATH, "//button[contains(text(),'Guardar')]").click()
            self.save_screenshot("crear_habitacion_valida.png")

            success_msg = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
            self.assertIn("Habitación creada", success_msg.text)
        except Exception as e:
            self.save_screenshot("crear_habitacion_error.png")
            raise e

    # ----------------------------------------------------------
    # 🔹 Caso 2: Crear habitación con datos inválidos
    # ----------------------------------------------------------
    def test_crear_habitacion_invalida(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/rooms/add/")
        try:
            # Dejar un campo vacío
            numero = self.wait.until(EC.presence_of_element_located((By.NAME, "room_number")))
            tipo = driver.find_element(By.NAME, "room_type")

            numero.send_keys("")  # vacío
            tipo.send_keys("Suite")

            driver.find_element(By.XPATH, "//button[contains(text(),'Guardar')]").click()
            self.save_screenshot("crear_habitacion_invalida.png")

            # Esperar un mensaje de error
            error_msg = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-danger")))
            self.assertIn("error", error_msg.text.lower())
        except Exception as e:
            self.save_screenshot("crear_habitacion_invalida_fail.png")
            raise e

    # ----------------------------------------------------------
    # 🔹 Caso 3: Editar habitación existente
    # ----------------------------------------------------------
    def test_editar_habitacion(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/rooms/")
        try:
            # Buscar botón editar
            edit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Editar')]")))
            edit_button.click()

            # Cambiar el precio
            precio = self.wait.until(EC.presence_of_element_located((By.NAME, "price")))
            precio.clear()
            precio.send_keys("300000")
            driver.find_element(By.XPATH, "//button[contains(text(),'Guardar')]").click()

            self.save_screenshot("editar_habitacion.png")

            success_msg = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))
            self.assertIn("actualizada", success_msg.text.lower())
        except Exception as e:
            self.save_screenshot("editar_habitacion_error.png")
            raise e

    # ----------------------------------------------------------
    # 🔹 Caso 4: Eliminar habitación
    # ----------------------------------------------------------
    def test_eliminar_habitacion(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/rooms/")
        try:
            delete_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Eliminar')]")))
            delete_button.click()

            # Confirmar en el popup o redirección
            self.save_screenshot("eliminar_habitacion.png")
            time.sleep(2)
        except Exception as e:
            self.save_screenshot("eliminar_habitacion_error.png")
            raise e

    @classmethod
    def tearDownClass(cls):
        """Cerrar navegador"""
        cls.save_screenshot("final_estado.png")
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
