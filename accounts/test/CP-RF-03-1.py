"""
CP-RF-03-1: Cambio con datos correctos
Entrada: Contraseña actual válida y nueva contraseña confirmada
Salida esperada: Mensaje "Contraseña actualizada correctamente"
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración - USAR USUARIO EXISTENTE
BASE_URL = "http://127.0.0.1:8000"
LOGIN_PATH = "/accounts/login/"
PW_CHANGE_PATH = "/accounts/password_change/"
USERNAME = "prueba"  # Cambiar por el usuario que existe en tu BD
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
        
        # Esperar a que cargue la página de login
        time.sleep(2)
        
        # Verificar que estamos en la página de login
        if "login" not in driver.current_url.lower():
            print("⚠️ No estamos en la página de login")
            driver.get(BASE_URL + LOGIN_PATH)
            time.sleep(2)
        
        # Buscar campos de forma más flexible
        username_fields = driver.find_elements(By.NAME, "username")
        if not username_fields:
            username_fields = driver.find_elements(By.ID, "id_username")
        if not username_fields:
            username_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        
        if username_fields:
            username_fields[0].clear()
            username_fields[0].send_keys(username)
            print(f"   ✅ Campo username encontrado y llenado")
        else:
            print("❌ No se pudo encontrar campo username")
            return False

        # Buscar campo password
        password_fields = driver.find_elements(By.NAME, "password")
        if not password_fields:
            password_fields = driver.find_elements(By.ID, "id_password")
        if not password_fields:
            password_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        
        if password_fields:
            password_fields[0].clear()
            password_fields[0].send_keys(password)
            print(f"   ✅ Campo password encontrado y llenado")
        else:
            print("❌ No se pudo encontrar campo password")
            return False

        # Buscar botón de submit
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
        if not buttons:
            buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        if not buttons:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        
        if buttons:
            buttons[0].click()
            print("   ✅ Botón de login clickeado")
        else:
            print("❌ No se pudo encontrar botón de submit")
            return False
        
        # Esperar y verificar resultado
        time.sleep(3)
        
        # Verificar si el login fue exitoso
        if "login" in driver.current_url.lower():
            print("❌ Login fallido - todavía en página de login")
            # Tomar screenshot para debug
            driver.save_screenshot("login_failed.png")
            print("📸 Screenshot guardado como login_failed.png")
            return False
        else:
            print("✅ Login exitoso - redirigido a otra página")
            return True
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        driver.save_screenshot("login_error.png")
        return False

def change_password(driver, wait, old_pw, new_pw, confirm_pw):
    try:
        print("🔄 Procesando cambio de contraseña...")
        driver.get(BASE_URL + PW_CHANGE_PATH)
        
        time.sleep(2)
        
        # Verificar que estamos en la página correcta
        if "password_change" not in driver.current_url:
            print("⚠️ No estamos en la página de cambio de contraseña")
            print(f"   URL actual: {driver.current_url}")
        
        # Buscar campos del formulario
        old_password_field = driver.find_element(By.NAME, "old_password")
        old_password_field.clear()
        old_password_field.send_keys(old_pw)
        
        new_password1_field = driver.find_element(By.NAME, "new_password1")
        new_password1_field.clear()
        new_password1_field.send_keys(new_pw)
        
        new_password2_field = driver.find_element(By.NAME, "new_password2")
        new_password2_field.clear()
        new_password2_field.send_keys(confirm_pw)
        
        # Buscar y hacer click en botón de submit
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_btn.click()
        
        print("✅ Formulario de cambio de contraseña enviado")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"❌ Error en cambio de contraseña: {e}")
        driver.save_screenshot("change_password_error.png")
        return False

def logout(driver):
    try:
        # Intentar diferentes formas de logout
        logout_links = driver.find_elements(By.LINK_TEXT, "Logout")
        if not logout_links:
            logout_links = driver.find_elements(By.LINK_TEXT, "logout")
        if not logout_links:
            logout_links = driver.find_elements(By.LINK_TEXT, "Cerrar sesión")
        if not logout_links:
            logout_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Logout")
        
        if logout_links:
            logout_links[0].click()
            print("✅ Logout exitoso")
            time.sleep(2)
        else:
            # Fallback: limpiar cookies y ir a logout URL
            driver.delete_all_cookies()
            driver.get(BASE_URL + "/accounts/logout/")
            print("⚠️ Logout por cookies")
    except Exception as e:
        print(f"⚠️ Error en logout: {e}")
        driver.delete_all_cookies()

def check_success_message(driver):
    page_text = driver.page_source.lower()
    success_indicators = [
        "contraseña actualizada", "password changed", "success", "éxito", 
        "actualizada correctamente", "cambio exitoso", "successfully"
    ]
    return any(indicator in page_text for indicator in success_indicators)

def main():
    print("="*60)
    print("CP-RF-03-1: CAMBIO CON DATOS CORRECTOS")
    print("="*60)
    
    driver, wait = setup_driver()
    NEW_PASSWORD = "NewStrongPass1"
    test_passed = False

    try:
        # 1. Login con contraseña antigua
        print("\n1. Verificando login con contraseña actual...")
        if not login(driver, wait, USERNAME, OLD_PASSWORD):
            print("❌ FALLÓ: No se pudo iniciar sesión inicialmente")
            print(f"   URL actual: {driver.current_url}")
            return False
        
        print(f"   ✅ Login exitoso. Página actual: {driver.current_url}")
        
        # 2. Cambiar contraseña
        print("\n2. Cambiando contraseña...")
        if not change_password(driver, wait, OLD_PASSWORD, NEW_PASSWORD, NEW_PASSWORD):
            print("❌ FALLÓ: No se pudo completar el cambio de contraseña")
            return False
        
        # 3. Verificar mensaje de éxito
        print("\n3. Verificando resultado...")
        if check_success_message(driver):
            print("✅ PASÓ: Mensaje de éxito detectado en la página")
        elif "/password_change/done/" in driver.current_url:
            print("✅ PASÓ: URL de confirmación detectada")
        else:
            print("⚠️ AVISO: Cambio completado pero sin confirmación clara")
            print(f"   URL actual: {driver.current_url}")
        
        # 4. Logout
        print("\n4. Cerrando sesión...")
        logout(driver)
        
        # 5. Verificar nueva contraseña funciona
        print("\n5. Verificando nueva contraseña...")
        if not login(driver, wait, USERNAME, NEW_PASSWORD):
            print("❌ FALLÓ: No se pudo iniciar sesión con nueva contraseña")
            return False
        
        print("✅ PASÓ: Nueva contraseña funciona correctamente")
        
        # 6. Restaurar contraseña original para otras pruebas
        print("\n6. Restaurando contraseña original...")
        if change_password(driver, wait, NEW_PASSWORD, OLD_PASSWORD, OLD_PASSWORD):
            print("✅ Contraseña restaurada para pruebas siguientes")
        
        test_passed = True
        print("\n🎉 **CP-RF-03-1: PASÓ EXITOSAMENTE**")
        
    except Exception as e:
        print(f"❌ FALLÓ: Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if test_passed:
            driver.save_screenshot("test_exitoso.png")
            print("📸 Screenshot de éxito guardado como test_exitoso.png")
        driver.quit()
        return test_passed

if __name__ == "__main__":
    print("🚀 INICIANDO CP-RF-03-1: Cambio con datos correctos")
    print(f"📝 Usuario: {USERNAME}")
    print(f"🔗 Servidor: {BASE_URL}")
    print("⏳ Por favor espera...")
    
    result = main()
    
    print("\n" + "="*50)
    if result:
        print("✅ CP-RF-03-1: PRUEBA EXITOSA")
    else:
        print("❌ CP-RF-03-1: PRUEBA FALLIDA")
    print("="*50)