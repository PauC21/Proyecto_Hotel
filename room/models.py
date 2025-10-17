from django.db import models
from django.utils import timezone
from datetime import datetime, time as dtime

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('occupied', 'Ocupada'),
        ('maintenance', 'En mantenimiento'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Habitación {self.room_number} ({self.get_status_display()})"

    @property
    def is_under_maintenance(self) -> bool:
        """Conveniencia: True cuando el status es 'maintenance'."""
        return str(self.status) == 'maintenance'

    def _as_datetime(self, value):
        """
        Convierte una fecha (date) o datetime a datetime 'aware' usando la zona local,
        colocando la hora a mediodía si solo se recibe una fecha.
        """
        if value is None:
            return None
        if isinstance(value, datetime):
            # si es naive, lo hacemos aware con timezone.localtime()
            if timezone.is_naive(value):
                return timezone.make_aware(value, timezone.get_current_timezone())
            return value
        # asumimos que es date -> convertir a datetime a las 12:00 para evitar problemas de zona
        return timezone.make_aware(datetime.combine(value, dtime(12, 0, 0)), timezone.get_current_timezone())

    @property
    def is_booked_now(self) -> bool:
        """
        True si existe alguna reserva activa (no cancelada) cuyo intervalo
        incluye el momento actual.
        """
        now = timezone.now()

        qs = getattr(self, "reservation_set", None)
        if qs is None:
            return False

        # excluir reservas canceladas
        active_reservations = qs.exclude(status='cancelled')

        for reservation in active_reservations.all():
            start = reservation.check_in_date
            end = reservation.check_out_date

            # normalizamos a datetimes aware (si usas date o datetime)
            if getattr(start, 'hour', None) is None:
                start_dt = timezone.make_aware(datetime.combine(start, dtime(12, 0, 0)), timezone.get_current_timezone())
            else:
                start_dt = start if timezone.is_aware(start) else timezone.make_aware(start, timezone.get_current_timezone())

            if getattr(end, 'hour', None) is None:
                end_dt = timezone.make_aware(datetime.combine(end, dtime(12, 0, 0)), timezone.get_current_timezone())
            else:
                end_dt = end if timezone.is_aware(end) else timezone.make_aware(end, timezone.get_current_timezone())

            if start_dt <= now <= end_dt:
                return True

        return False
