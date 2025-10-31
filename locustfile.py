# locustfile.py
from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import os
from datetime import date, timedelta

# ----------------- Ajusta si quieres via env vars -----------------
USERNAME = os.getenv("LOCUST_USER", "testuser")
PASSWORD = os.getenv("LOCUST_PASS", "testpass")
LOGIN_URL = os.getenv("LOCUST_LOGIN_URL", "/accounts/login/")
PROFILE_URL = os.getenv("LOCUST_PROFILE_URL", "/accounts/profile/")
DASHBOARD_URL = os.getenv("LOCUST_DASHBOARD_URL", "/")  # Dashboard en la raíz
EXPORT_PDF_URL = os.getenv("LOCUST_EXPORT_PDF_URL", "/reports/export/pdf/")
EXPORT_EXCEL_URL = os.getenv("LOCUST_EXPORT_EXCEL_URL", "/reports/export/excel/")
# -----------------------------------------------------------------

def default_date_range(days_back=30):
    """
    Rango por defecto usado para exports. Si tus datos están en meses
    anteriores, incrementa days_back (p. ej. 365).
    """
    end = date.today()
    start = end - timedelta(days=days_back)
    return start.isoformat(), end.isoformat()


class BaseUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Realiza login en cada usuario virtual:
        1) GET /accounts/login/ para obtener csrf token (si existe) y cookie de sesión.
        2) POST con datos (form-data) incluyendo csrfmiddlewaretoken si se detecta.
        3) Verificar perfil para confirmar sesión.
        """
        # 1) GET login
        r = self.client.get(LOGIN_URL, name="get-login")
        if r.status_code != 200:
            print(f"[WARN] GET {LOGIN_URL} returned {r.status_code}")

        csrf_token = None
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            token_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
            if token_input:
                csrf_token = token_input.get("value")
        except Exception:
            csrf_token = None

        # 2) POST credentials (form-data)
        data = {"username": USERNAME, "password": PASSWORD}
        headers = {"Referer": r.url if hasattr(r, "url") else LOGIN_URL}
        if csrf_token:
            data["csrfmiddlewaretoken"] = csrf_token

        post_resp = self.client.post(LOGIN_URL, data=data, headers=headers, allow_redirects=True, name="login")
        # fallback: intentar JSON si la app expone API
        if post_resp.status_code not in (200, 201, 302):
            post_json = self.client.post(LOGIN_URL, json={"username": USERNAME, "password": PASSWORD}, name="login-json")
            if post_json.status_code in (200, 201, 302):
                # si devuelve token en JSON, setear header Authorization
                try:
                    token = post_json.json().get("token")
                    if token:
                        self.client.headers.update({"Authorization": f"Bearer {token}"})
                except Exception:
                    pass
            else:
                print(f"[ERROR] Login failed: form_status={post_resp.status_code}, json_status={(post_json.status_code if post_json is not None else 'none')}")

        # 3) verificar perfil para confirmar sesión (no lo marcamos fatal, solo aviso)
        prof = self.client.get(PROFILE_URL, name="check-profile")
        if prof.status_code not in (200, 302):
            print(f"[WARN] Profile check returned {prof.status_code} after login.")

# ----------------- Scenario: Dashboard (HU-LT-15) -----------------
class DashboardUser(BaseUser):
    weight = 50

    @task
    def view_dashboard(self):
        with self.client.get(DASHBOARD_URL, name="GET / (dashboard)", catch_response=True) as resp:
            # Si redirige a login o incluye 'login' en HTML, es falta de sesión
            if resp.status_code in (302, 401, 403) or ("login" in resp.text.lower() and "dashboard" not in resp.text.lower()):
                resp.failure(f"Not authenticated or redirect (status {resp.status_code})")
                return
            if resp.status_code != 200:
                resp.failure(f"Unexpected status {resp.status_code}")
                return
            low = resp.text.lower()
            if not any(k in low for k in ("reservas", "reservations", "rooms_count", "guests_count", "reservations_count", "total reservas", "dashboard")):
                # No marcamos fatal si el HTML varía, pero sí lo registramos como fallo para investigar.
                resp.failure("dashboard response missing expected summary fields")

# ----------------- Scenario: Export PDF (HU-LT-16) -----------------
class ExportPDFUser(BaseUser):
    weight = 5

    @task
    def export_pdf(self):
        start, end = default_date_range(30)
        params = {"start": start, "end": end}
        with self.client.get(EXPORT_PDF_URL, params=params, name="GET /reports/export/pdf/", stream=True, catch_response=True) as resp:
            # Si redirige a login, marcar fallo de autenticación
            if resp.status_code in (401, 403) or ("login" in resp.text.lower()):
                resp.failure(f"Auth/redirect problem status {resp.status_code}")
                return

            # 302 -> tu vista hace redirect (por ejemplo si no hay reservas en el rango)
            if resp.status_code == 302:
                # Tratar como caso esperado: log y success (no contamos como failure)
                # Puedes inspeccionar 'Location' header si quieres
                location = resp.headers.get("Location", "")
                resp.success()
                return

            # Si es 200, comprobar tipo/encabezados
            if resp.status_code != 200:
                resp.failure(f"PDF export status {resp.status_code}")
                return

            # Preferir Content-Type header
            ct = resp.headers.get("Content-Type", "")
            if "pdf" in ct.lower():
                resp.success()
                return

            # Fallback: comprobar firma de PDF (%PDF)
            if resp.content and resp.content[:4] == b"%PDF":
                resp.success()
            else:
                snippet = resp.content[:300]
                resp.failure(f"Response doesn't look like a PDF (missing %PDF header). snippet={snippet}")

# ----------------- Scenario: Export Excel (HU-LT-17) -----------------
class ExportExcelUser(BaseUser):
    weight = 5

    @task
    def export_excel(self):
        start, end = default_date_range(30)
        params = {"start": start, "end": end}
        with self.client.get(EXPORT_EXCEL_URL, params=params, name="GET /reports/export/excel/", stream=True, catch_response=True) as resp:
            if resp.status_code in (401, 403) or ("login" in resp.text.lower()):
                resp.failure(f"Auth/redirect problem status {resp.status_code}")
                return

            if resp.status_code == 302:
                # Redirect (probablemente "no data") -> tratamos como caso esperado
                resp.success()
                return

            if resp.status_code != 200:
                resp.failure(f"Excel export status {resp.status_code}")
                return

            ct = resp.headers.get("Content-Type", "")
            if any(x in ct.lower() for x in ("excel", "spreadsheet", "openxmlformats")):
                resp.success()
                return

            # Fallback: xlsx empieza por bytes 'PK'
            if resp.content and resp.content[:2] == b"PK":
                resp.success()
            else:
                snippet = resp.content[:300]
                resp.failure(f"Response doesn't look like an xlsx (missing PK header). snippet={snippet}")
