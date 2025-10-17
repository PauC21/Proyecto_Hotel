# guest/forms.py
from django import forms
from .models import Guest
from django.core.exceptions import ValidationError


class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["first_name", "last_name", "email", "phone_number", "government_id", "address"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "phone_number": "Teléfono",
            "government_id": "Documento de identidad",
            "address": "Dirección",
        }

    def clean_government_id(self):
        gov = self.cleaned_data.get('government_id')
        if not gov:
            return gov
        gov = gov.strip()
        # normalizar (opcional): quitar espacios, mayúsculas, etc.
        # gov = gov.replace(" ", "").upper()

        # Si estamos en edición (instance existe) permitimos el mismo valor actual
        qs = Guest.objects.filter(government_id=gov)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Ya existe un cliente con ese documento.")
        return gov    