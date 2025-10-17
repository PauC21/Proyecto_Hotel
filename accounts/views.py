from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from .forms import ProfileForm
from .forms import StyledPasswordChangeForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile_update.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        # El usuario solo puede editar su propio perfil
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)

class PasswordUpdateView(LoginRequiredMixin, PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("password-change-done")

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña se actualizó correctamente.")
        return super().form_valid(form)
    


def custom_logout(request):
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("login")

@login_required
def ProfileView(request):
    return render(request, 'accounts/profile.html')