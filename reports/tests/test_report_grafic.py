import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class ReportGraphsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")  # descomenta si quieres headless
        chrome_options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.base_url = "http://127.0.0.1:8000/"  # cambia si usas otra URL/puerto
        # carpeta de screenshots (asegúrate que exista)
        cls.screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(cls.screenshots_dir, exist_ok=True)
        cls.wait = WebDriverWait(cls.driver, 10)

    def test_generar_reporte_con_grafico(self):
        driver = self.driver
        wait = self.wait

        # 1) Abrir la página de login (ajusta la ruta si es otra)
        driver.get(self.base_url + "login/")

        # --- Ajusta estos selectores si tu formulario es diferente ---
        # campos: name="username" y name="password"
        # botón de login: button[type='submit'] o un input con value "Log in"
        try:
            username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password = driver.find_element(By.NAME, "password")
        except Exception:
            # fallback: intenta por id
            username = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
            password = driver.find_element(By.ID, "id_password")

        # 2) Credenciales (ajusta a un usuario existente en tu BD)
        username.clear()
        username.send_keys("admin")          # <-- CAMBIAR si tu usuario es distinto
        password.clear()
        password.send_keys("admin123")       # <-- CAMBIAR por la contraseña correcta

        # Click en login
        try:
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        except Exception:
            driver.find_element(By.XPATH, "//input[@type='submit' or @value='Log in']").click()

        # 3) Esperar a que el panel cargue (ej: una url que contenga 'dashboard' o un elemento del menú)
        wait.until(EC.url_contains("dashboard"))

        # 4) Navegar al módulo "Reportes" (ajusta selector si tu menú es distinto)
        # ejemplos de localizadores:
        # - link text: "Reportes"
        # - path en menú: a[href*="/reports/"]
        try:
            reports_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Reportes")))
            reports_link.click()
        except Exception:
            # fallback: buscar por URL parcial
            driver.get(self.base_url + "reports/")

        # 5) Esperar que cargue la página de reportes (ej: un título o el formulario)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # 6) Rellenar rango de fechas y tipo de reporte (ajusta los nombres / ids)
        # Ejemplo: inputs con name="start_date" y "end_date", y select id="report_type"
        try:
            start = driver.find_element(By.NAME, "start_date")
            end = driver.find_element(By.NAME, "end_date")
        except Exception:
            # fallback por id
            start = driver.find_element(By.ID, "id_start_date")
            end = driver.find_element(By.ID, "id_end_date")

        # Usa fechas donde sabes que hay datos en la BD
        start.clear(); start.send_keys("2025-10-01")
        end.clear(); end.send_keys("2025-10-31")

        # Seleccionar tipo de reporte (ejemplo)
        try:
            report_select = driver.find_element(By.ID, "report_type")
            for option in report_select.find_elements(By.TAG_NAME, "option"):
                if "Ocupación" in option.text or "ocupacion" in option.text.lower():
                    option.click()
                    break
        except Exception:
            # si no hay select, intenta marcar radio o checkbox
            pass

        # 7) Click en "Generar reporte"
        try:
            gen_btn = driver.find_element(By.XPATH, "//button[contains(., 'Generar') or contains(., 'Generar reporte') or contains(., 'Generate')]")
            gen_btn.click()
        except Exception:
            # fallback: botón por id
            try:
                driver.find_element(By.ID, "generate_report").click()
            except Exception:
                raise AssertionError("No se encontró el botón Generar reporte - ajusta el selector en el test")

        # 8) Esperar que el gráfico aparezca.
        # Normalmente los gráficos pueden ser <canvas>, <svg> o <div class="chart">.
        grafico = None
        try:
            grafico = wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
        except Exception:
            try:
                grafico = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg")))
            except Exception:
                try:
                    grafico = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".chart, .grafico, #chart")))
                except Exception:
                    pass

        # 9) Validaciones básicas
        self.assertIsNotNone(grafico, "No se detectó ningún gráfico; revisa selectores y que existan datos en el periodo.")

        # 10) Esperar un segundo y tomar captura
        time.sleep(1)
        screenshot_path = os.path.join(self.screenshots_dir, "report_graph.png")
        driver.save_screenshot(screenshot_path)
        print("Captura guardada en:", screenshot_path)

        # (opcional) validar que el canvas tenga ancho/alto via JS
        try:
            if grafico.tag_name.lower() == "canvas":
                w = driver.execute_script("return arguments[0].width;", grafico)
                h = driver.execute_script("return arguments[0].height;", grafico)
                self.assertTrue(w > 10 and h > 10, "Canvas muy pequeño, posible gráfico no renderizado")
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
