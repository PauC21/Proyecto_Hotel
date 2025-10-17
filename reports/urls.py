from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportHomeView.as_view(), name='reports-home'),
    path('export/pdf/', views.export_report_pdf, name='reports-export-pdf'),
    path('export/excel/', views.export_report_excel, name='reports-export-excel'),
]