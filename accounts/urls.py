from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import ProfileUpdateView
from .views import PasswordUpdateView

urlpatterns = [
    path("password_update/", views.PasswordUpdateView.as_view(), name='password-update'),
    path("profile/", views.ProfileView, name='profile'),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),

    # Login / Logout
    path("login/", auth_views.LoginView.as_view(template_name='registration/login.html'), name="login"),
    path("logout/", views.custom_logout, name="logout"), 

    #actualizar contraseña
    path("password/update/", PasswordUpdateView.as_view(), name="password-update"),
    path("password/done/",auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),name="password-change-done",),
]