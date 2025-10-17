from django.urls import path
from .views import GuestListView, GuestDetailView, GuestCreateView, guest_update, guest_delete
from . import views

urlpatterns = [
    path('guests/create/', GuestCreateView.as_view(), name="guest_create"),
    path('guests/', GuestListView.as_view(), name='guest_list'),
    path('guests/<int:pk>/', GuestDetailView.as_view(), name='guest_detail'),
    path('guests/<int:pk>/update/', guest_update, name="guest_update"),
    path('guests/<int:pk>/delete/', guest_delete, name="guest_delete"),
]
