import time
import os
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class LogoutTest(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)
        
        # Crear directorio para screenshots si no existe
        os.makedirs("screenshots", exist_ok=True)

    def test_cerrar_sesion(self):
        driver = self.driver
        wait = self.wait

        try:
            # 1️⃣ Navegar al login
            print("🔗 Navegando a la página de login...")
            driver.get("http://127.0.0.1:8000/accounts/login/")  # URL corregida
            time.sleep(2)
            
            # Debug: Capturar la página inicial
            driver.save_screenshot("screenshots/0_pagina_inicial.png")
            print(f"📍 URL actual: {driver.current_url}")
            
            # 2️⃣ Buscar campos de login de forma flexible
            print("🔍 Buscando campos de login...")
            
            # Intentar encontrar campo username
            username_field = None
            try:
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            except:
                try:
                    username_field = driver.find_element(By.ID, "id_username")
                except:
                    username_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            
            # Intentar encontrar campo password
            password_field = None
            try:
                password_field = driver.find_element(By.NAME, "password")
            except:
                try:
                    password_field = driver.find_element(By.ID, "id_password")
                except:
                    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            # 3️⃣ Iniciar sesión
            print("🔑 Iniciando sesión...")
            username_field.clear()
            username_field.send_keys("prueba")
            
            password_field.clear()
            password_field.send_keys("ejemplo123+")
            
            # Buscar botón de submit
            submit_button = None
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            
            submit_button.click()
            time.sleep(3)
            
            driver.save_screenshot("screenshots/1_despues_login.png")
            print(f"📍 URL después de login: {driver.current_url}")

            # 4️⃣ Verificar que haya iniciado correctamente
            self.assertNotIn("login", driver.current_url.lower(), 
                           "No se pudo iniciar sesión correctamente")
            print("✅ Login exitoso")

            # 5️⃣ Buscar y hacer clic en "Cerrar sesión"
            print("🚪 Buscando opción de cerrar sesión...")
            logout_link = None
            
            try:
                logout_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Cerrar sesión")))
            except:
                try:
                    logout_link = driver.find_element(By.LINK_TEXT, "Logout")
                except:
                    try:
                        logout_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Cerrar")
                    except:
                        logout_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Logout")
            
            driver.save_screenshot("screenshots/2_antes_logout.png")
            logout_link.click()
            time.sleep(2)
            
            driver.save_screenshot("screenshots/3_despues_logout.png")
            print(f"📍 URL después de logout: {driver.current_url}")

            # 6️⃣ Comprobar redirección al login
            self.assertIn("login", driver.current_url.lower(), 
                         "No se redirigió correctamente al login")
            print("✅ Redirección a login correcta")

            # 7️⃣ Intentar volver atrás (no debe acceder)
            print("⬅️ Intentando volver atrás...")
            driver.back()
            time.sleep(2)
            
            driver.save_screenshot("screenshots/4_despues_back.png")
            print(f"📍 URL después de back: {driver.current_url}")
            
            self.assertIn("login", driver.current_url.lower(),
                         "La sesión no se cerró correctamente - pudo volver atrás")
            print("✅ No se puede volver atrás - sesión cerrada correctamente")

            # Captura final de éxito
            driver.save_screenshot("screenshots/test_logout_exitoso.png")
            print("🎉 Test de logout completado exitosamente")
            
        except Exception as e:
            print(f"❌ Error durante el test: {e}")
            driver.save_screenshot("screenshots/test_logout_error.png")
            
            # Información adicional para debugging
            print(f"📍 URL actual: {driver.current_url}")
            print(f"📄 Título de página: {driver.title}")
            
            # Mostrar campos disponibles en la página
            print("\n🔍 Campos de input encontrados:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                print(f"  - Type: {inp.get_attribute('type')}, "
                      f"Name: {inp.get_attribute('name')}, "
                      f"ID: {inp.get_attribute('id')}")
            
            raise

    def tearDown(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    print("🚀 Iniciando test de logout...")
    unittest.main(verbosity=2)