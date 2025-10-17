from django.test import TestCase
from django.utils import timezone
from notifications.signals import (_guest_email, _guest_phone, _guest_name, _room_label, _format_datetime, _build_message)
from guest.models import Guest
from room.models import Room
from main.models import Reservation


class NotificationHelpersTests(TestCase):

    def build_message(prefix, instance: Reservation):
        g = instance.guest
        r = instance.room
        check_in_date = getattr(instance, "check_in_date", None)
        check_out_date = getattr(instance, "check_out_date", None)
        status = getattr(instance, "status", "-")

    # incluir prefix en la primera línea para que el texto muestre el tipo de notificación
        lines = [f"{prefix}"]

        lines += [
        "Hola....esta es la información que tenemos sobre tu estadia con nosotros",
        f"Huésped: {_guest_name(g)}",
        f"Habitación: {_room_label(r)}",
        f"Check-in: {_format_datetime(check_in_date)}",
        f"Check-out: {_format_datetime(check_out_date)}",
        f"Estado: {status}",
        f"Fecha aviso: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    ]
        return "\n".join(lines)


