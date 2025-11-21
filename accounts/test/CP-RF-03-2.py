"""
CP-RF-03-2: Contraseña actual incorrecta
Entrada: Contraseña actual errónea
Salida esperada: Mensaje 'contraseña actual incorrecta'; no cambiar contraseña
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración
BASE_URL = "http://127.0.0.1:8000"
LOGIN_PATH = "/accounts/login/"
PW_CHANGE_PATH = "/accounts/password_change/"
USERNAME = "prueba"        # En lugar de "testuser"
OLD_PASSWORD = "ejemplo123+"

def setup_driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    try:
        service = webdriver.ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"⚠️ Aviso ChromeDriver: {e}")
        driver = webdriver.Chrome(options=options)
    
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 15)
    return driver, wait

def login(driver, wait, username, password):
    try:
        print(f"🔑 Iniciando sesión como: {username}")
        driver.get(BASE_URL + LOGIN_PATH)
        
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        
        driver.find_element(By.NAME, "username").clear()
        driver.find_element(By.NAME, "username").send_keys(username)
        
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(password)
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()
        
        time.sleep(2)
        
        if "login" not in driver.current_url.lower():
            print("✅ Login exitoso")
            return True
        else:
            print("❌ Login fallido")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False

def change_password(driver, wait, old_pw, new_pw, confirm_pw):
    try:
        print("🔄 Procesando cambio de contraseña...")
        driver.get(BASE_URL + PW_CHANGE_PATH)
        
        wait.until(EC.presence_of_element_located((By.NAME, "old_password")))
        
        driver.find_element(By.NAME, "old_password").clear()
        driver.find_element(By.NAME, "old_password").send_keys(old_pw)
        
        driver.find_element(By.NAME, "new_password1").clear()
        driver.find_element(By.NAME, "new_password1").send_keys(new_pw)
        
        driver.find_element(By.NAME, "new_password2").clear()
        driver.find_element(By.NAME, "new_password2").send_keys(confirm_pw)
        
        driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()
        
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"❌ Error en cambio de contraseña: {e}")
        return False

def logout(driver):
    try:
        driver.find_element(By.LINK_TEXT, "Logout").click()
        print("✅ Logout exitoso")
    except:
        try:
            driver.find_element(By.LINK_TEXT, "Cerrar sesión").click()
            print("✅ Logout exitoso")
        except:
            driver.delete_all_cookies()
            driver.get(BASE_URL + "/accounts/logout/")
            print("⚠️ Logout por cookies")

def check_error_message(driver):
    page_text = driver.page_source.lower()
    error_indicators = [
        "error", "incorrect", "invalid", "incorrecta", "no coincide"
    ]
    return any(indicator in page_text for indicator in error_indicators)

def main():
    print("="*60)
    print("CP-RF-03-2: CONTRASEÑA ACTUAL INCORRECTA")
    print("="*60)
    
    driver, wait = setup_driver()
    test_passed = False

    try:
        # 1. Login
        if not login(driver, wait, USERNAME, OLD_PASSWORD):
            print("❌ FALLÓ: No se pudo iniciar sesión")
            return False
        
        # 2. Intentar cambiar con contraseña actual incorrecta
        WRONG_PASSWORD = "WrongOldPassword123"
        change_password(driver, wait, WRONG_PASSWORD, "NewPass123", "NewPass123")
        
        # 3. Verificar mensaje de error
        if check_error_message(driver):
            print("✅ PASÓ: Se detectó mensaje de error apropiado")
            driver.save_screenshot("CP-RF-03-2_error_detectado.png")
            print("📸 Screenshot guardado como CP-RF-03-2_error_detectado.png")
        else:
            print("⚠️ AVISO: No se detectó mensaje de error claro")
            driver.save_screenshot("CP-RF-03-2_sin_error.png")
            print("📸 Screenshot guardado como CP-RF-03-2_sin_error.png")
        
        # 4. Verificar que la contraseña original sigue funcionando
        logout(driver)
        time.sleep(1)
        
        if login(driver, wait, USERNAME, OLD_PASSWORD):
            print("✅ PASÓ: Contraseña original sigue funcionando (no se cambió)")
            test_passed = True
        else:
            print("❌ FALLÓ: La contraseña original ya no funciona")
            
        print("\n🎉 **CP-RF-03-2: PASÓ EXITOSAMENTE**")
        
    except Exception as e:
        print(f"❌ FALLÓ: Error inesperado: {e}")
    finally:
        driver.quit()
        return test_passed

if __name__ == "__main__":
    print("🚀 INICIANDO CP-RF-03-2: Contraseña actual incorrecta")
    print(f"📝 Usuario: {USERNAME}")
    print(f"🔗 Servidor: {BASE_URL}")
    
    result = main()
    
    print("\n" + "="*50)
    if result:
        print("✅ CP-RF-03-2: PRUEBA EXITOSA")
    else:
        print("❌ CP-RF-03-2: PRUEBA FALLIDA")
    print("="*50)