from django.urls import path
from . import views
from .views import ReservationDeleteView
from .views import ReservationCancelView


urlpatterns = [
    path('modd',views.Moddview.as_view(),name="modd"),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservation/create/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('reservation/<int:pk>/update', views.ReservationUpdateView.as_view(), name='reservation_update'),
    path('reservation/<int:pk>', views.ReservationDetailView.as_view(), name='reservation_detail'),
    path("reservation/<int:pk>/delete/", ReservationDeleteView.as_view(), name="reservation_delete"),
    path('room/<int:pk>/maintenance/', views.toggle_maintenance, name='toggle_maintenance'),
    path('reservation/<int:pk>/cancel/', ReservationCancelView.as_view(), name='reservation_cancel'),


]
