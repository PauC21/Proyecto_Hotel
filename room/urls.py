from django.urls import path
from .views import RoomListView, RoomDetailView, RoomCreateView
from . import views

urlpatterns = [
    path('rooms/create/', RoomCreateView.as_view(), name="room_create"),
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('<int:pk>/update/', views.room_update, name="room_update"),
    path('<int:pk>/delete/', views.room_delete, name="room_delete"),

]
