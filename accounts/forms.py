# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Tu nombre"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Tu apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com"}),
        }

class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["old_password"].widget.attrs.update({
            "class": "inputx", "placeholder": "Contraseña actual"
        })
        self.fields["new_password1"].widget.attrs.update({
            "class": "inputx", "placeholder": "Nueva contraseña"
        })
        self.fields["new_password2"].widget.attrs.update({
            "class": "inputx", "placeholder": "Confirmar nueva contraseña"
        })