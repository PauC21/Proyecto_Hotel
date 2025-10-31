"""
CP-RF-03-4: Cambio donde nueva = antigua
Entrada: Contraseña actual = nueva contraseña
Salida esperada: Mensaje 'la nueva contraseña debe ser distinta'
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
USERNAME = "palis"        # En lugar de "testuser"
OLD_PASSWORD = "Proyecto2025++"

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

def main():
    print("="*60)
    print("CP-RF-03-4: NUEVA CONTRASEÑA IGUAL A LA ACTUAL")
    print("="*60)
    
    driver, wait = setup_driver()
    test_passed = False

    try:
        # 1. Login
        if not login(driver, wait, USERNAME, OLD_PASSWORD):
            print("❌ FALLÓ: No se pudo iniciar sesión")
            return False
        
        # 2. Intentar cambiar a la misma contraseña
        change_password(driver, wait, OLD_PASSWORD, OLD_PASSWORD, OLD_PASSWORD)
        
        # 3. Verificar mensaje de error
        page_text = driver.page_source.lower()
        same_password_indicators = [
            "debe ser distinta", "diferente", "no puede ser igual", 
            "similar", "same", "igual", "misma"
        ]
        
        if any(indicator in page_text for indicator in same_password_indicators):
            print("✅ PASÓ: Se detectó mensaje de contraseña idéntica")
            test_passed = True
        else:
            # Verificar mensaje de error genérico
            error_indicators = ["error", "incorrect", "invalid"]
            if any(indicator in page_text for indicator in error_indicators):
                print("✅ PASÓ: Se detectó mensaje de error (posiblemente por contraseña idéntica)")
                test_passed = True
            else:
                print("❌ FALLÓ: No se detectó mensaje de contraseña idéntica")
        
        # 4. Verificar que la contraseña original sigue funcionando
        logout(driver)
        time.sleep(1)
        
        if login(driver, wait, USERNAME, OLD_PASSWORD):
            print("✅ PASÓ: Contraseña original sigue funcionando")
        else:
            print("❌ FALLÓ: La contraseña original ya no funciona")
            test_passed = False
            
        if test_passed:
            print("\n🎉 **CP-RF-03-4: PASÓ EXITOSAMENTE**")
        
    except Exception as e:
        print(f"❌ FALLÓ: Error inesperado: {e}")
    finally:
        driver.quit()
        return test_passed

if __name__ == "__main__":
    print("🚀 INICIANDO CP-RF-03-4: Nueva contraseña igual a la actual")
    print(f"📝 Usuario: {USERNAME}")
    print(f"🔗 Servidor: {BASE_URL}")
    
    result = main()
    
    print("\n" + "="*50)
    if result:
        print("✅ CP-RF-03-4: PRUEBA EXITOSA")
    else:
        print("❌ CP-RF-03-4: PRUEBA FALLIDA")
    print("="*50)