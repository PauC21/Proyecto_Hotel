from django import forms
from .models import Room
from django.utils import timezone
from django.core.exceptions import ValidationError
from main.models import Reservation



class CustomReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["guest", "room", "check_in_date", "check_out_date", "status"]
        widgets = {
            "check_in_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "check_out_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar input_formats para que parsee YYYY-MM-DD correctamente
        if "check_in_date" in self.fields:
            self.fields["check_in_date"].input_formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]
            # UX: evitar seleccionar fechas pasadas desde el navegador
            self.fields["check_in_date"].widget.attrs.setdefault("min", timezone.localdate().isoformat())
        if "check_out_date" in self.fields:
            self.fields["check_out_date"].input_formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]
            self.fields["check_out_date"].widget.attrs.setdefault("min", timezone.localdate().isoformat())

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in_date")
        check_out = cleaned.get("check_out_date")

        today = timezone.localdate()

        # Validar check_in no en pasado
        if check_in:
            # si es datetime, usar la parte date
            if hasattr(check_in, "date"):
                check_in_date = check_in.date()
            else:
                check_in_date = check_in

            if check_in_date < today:
                self.add_error("check_in_date", ValidationError("La fecha de llegada no puede ser anterior a la fecha actual."))

        # Validar check_out > check_in
        if check_in and check_out:
            if hasattr(check_out, "date"):
                check_out_date = check_out.date()
            else:
                check_out_date = check_out

            if check_out_date <= (check_in.date() if hasattr(check_in, "date") else check_in):
                self.add_error("check_out_date", ValidationError("La fecha de salida debe ser posterior a la fecha de llegada."))

        return cleaned

class RoomForm(forms.ModelForm):
    room_number = forms.CharField(label="Número de habitación")
    room_type = forms.CharField(label="Tipo de habitación")
    price_per_night = forms.DecimalField(label="Precio por noche")

    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night']