from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from reports.models import Reporte  # Ajusta el modelo si tu app usa otro nombre

class ExportReportTests(TestCase):

    def setUp(self):
        # Crear usuario autorizado
        self.user = User.objects.create_user(username='admin', password='admin123')
        self.client = Client()
        self.client.login(username='admin', password='admin123')

        # Crear un reporte de ejemplo
        Reporte.objects.create(
            nombre="Reporte de prueba",
            fecha=date(2025, 10, 22),
            descripcion="Reporte generado automáticamente para prueba"
        )

    def test_export_pdf_success(self):
        """CP-RF-06-1: Exportar reporte en formato PDF"""
        url = reverse('reports:export_pdf')  # Asegúrate de que coincida con tu nombre en urls.py
        response = self.client.get(url, {'start': '2025-10-01', 'end': '2025-10-31'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 100)  # hay contenido binario
        print("✅ Exportación PDF correcta")

    def test_export_excel_success(self):
        """CP-RF-06-2: Exportar reporte en formato Excel"""
        url = reverse('reports:export_excel')
        response = self.client.get(url, {'start': '2025-10-01', 'end': '2025-10-31'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response['Content-Type'])
        self.assertTrue(len(response.content) > 100)
        print("✅ Exportación Excel correcta")

    def test_export_no_data(self):
        """CP-RF-06-3: Exportar con periodo sin datos"""
        url = reverse('reports:export_pdf')
        response = self.client.get(url, {'start': '2025-01-01', 'end': '2025-01-02'})

        # Si el sistema maneja mensaje de error
        self.assertIn(response.status_code, [200, 400])
        content = response.content.decode('utf-8', errors='ignore')

        self.assertTrue(
            'No hay datos' in content or 'sin registros' in content or len(response.content) < 200,
            "Debe mostrar mensaje de 'No hay datos disponibles'"
        )
        print("✅ Exportación sin datos manejada correctamente")