# notifications/signals.py
from django.db.models.signals import post_save, post_delete
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import logging

from main.models import Reservation  # ajusta si tu app/modelo tiene otro path
from notifications.utils import notify_email, notify_sms, notify_whatsapp

logger = logging.getLogger(__name__)

def _guest_email(guest):
    return getattr(guest, "email", None) or getattr(getattr(guest, "user", None), "email", None)

def _guest_phone(guest):
    return getattr(guest, "phone_number", None)

def _guest_name(guest):
    return (getattr(guest, "name", None) or
            f"{getattr(guest, 'first_name', '')} {getattr(guest, 'last_name', '')}".strip() or
            "Huésped")

def _room_label(room):
    return getattr(room, "room_number", None) or getattr(room, "id", None) or "Habitación"

def _format_datetime(dt):
    return dt.strftime('%Y-%m-%d %H:%M') if dt else '-'

def _build_message(prefix, instance: Reservation):
    g = instance.guest
    r = instance.room
    check_in_date = getattr(instance, "check_in_date", None)
    check_out_date = getattr(instance, "check_out_date", None)
    status = getattr(instance, "status", "-")
    lines = [
        f"Hola....esta es la información que tenemos sobre tu estadia con nosotros",
        f"Huésped: {_guest_name(g)}",
        f"Habitación: {_room_label(r)}",
        f"Check-in: {_format_datetime(check_in_date)}",
        f"Check-out: {_format_datetime(check_out_date)}",
        f"Estado: {status}",
        f"Fecha aviso: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    ]
    return "\n".join(lines)

def _notify(instance: Reservation, prefix: str):
    guest = instance.guest
    subject = f"{prefix} - Hotel AJP Inn"
    message = _build_message(prefix, instance)

    # correo
    email = _guest_email(guest)
    if email:
        try:
            notify_email(email, subject, message)
            logger.info("Email enviado a %s - %s", email, prefix)
        except Exception:
            logger.exception("Error enviando email para reserva %s", instance.pk)

    # whatsapp
    phone = _guest_phone(guest)
    if phone:
        try:
            notify_whatsapp(phone, f"{subject}\n\n{message}")
            logger.info("WhatsApp enviado a %s - %s", phone, prefix)
        except Exception:
            logger.exception("Error enviando WhatsApp para reserva %s", instance.pk)

def _send_checkout_receipt(instance: Reservation):
    """
    Mensaje más detallado en el check-out (recibo en texto).
    """
    guest = instance.guest
    room_label = _room_label(instance.room)

    subject = f"Recibo de salida - Reserva #{instance.pk} - Hotel AJP Inn"
    lines = [
        "Gracias por hospedarse en Hotel AJP Inn 🌿",
        "-------------------------------------",
        f"Reserva: {instance.pk}",
        f"Huésped: {_guest_name(guest)}",
        f"Documento: {getattr(guest, 'government_id', '')}",
        f"Habitación: {room_label}",
        f"Check-in: {_format_datetime(getattr(instance, 'check_in_date', None))}",
        f"Check-out: {_format_datetime(getattr(instance, 'check_out_date', None))}",
    ]

    total = getattr(instance, 'total_price', None) or getattr(instance, 'price', None)
    if total:
        lines.append(f"Total: {total}")

    lines += [
        "-------------------------------------",
        f"Fecha de salida: {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Esperamos que haya tenido una excelente estadía 💫 ¡Vuelva pronto!",
    ]

    text = "\n".join(lines)

    # enviar correo
    email = _guest_email(guest)
    if email:
        try:
            notify_email(email, subject, text)
            logger.info("Recibo (email) enviado a %s para reserva %s", email, instance.pk)
        except Exception:
            logger.exception("Error enviando recibo por email para reserva %s", instance.pk)

    # enviar whatsapp
    phone = _guest_phone(guest)
    if phone:
        try:
            notify_whatsapp(phone, subject + "\n\n" + text)
            logger.info("Recibo (whatsapp) enviado a %s para reserva %s", phone, instance.pk)
        except Exception:
            logger.exception("Error enviando recibo por WhatsApp para reserva %s", instance.pk)


# -------------------- Señales --------------------
@receiver(pre_save, sender=Reservation)
def _cache_old_status(sender, instance, **kwargs):
    """
    Guarda el estado anterior para poder compararlo en post_save.
    Esto evita queries extra en post_save para leer el 'old' desde BD.
    """
    if not instance.pk:
        # creación: no hay estado previo
        instance._old_status = None
        return
    try:
        old = Reservation.objects.get(pk=instance.pk)
        instance._old_status = getattr(old, "status", None)
    except Reservation.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Reservation)
def reservation_saved(sender, instance, created, **kwargs):
    """
    Maneja notificaciones tras crear o actualizar una reserva.
      - Si created -> notificar "Reserva creada"
      - Si updated and status cambió -> notificar según nuevo estado (incluye check_out)
      - Si updated and simple cambio de campos -> notificar "Reserva actualizada"
    """
    try:
        if created:
            _notify(instance, "Reserva creada")
            return

        # updated
        old_status = getattr(instance, "_old_status", None)
        new_status = getattr(instance, "status", None)

        # si cambió a check_out -> enviar recibo (y no la notificación genérica)
        if old_status != 'check_out' and new_status == 'check_out':
            _send_checkout_receipt(instance)
            return

        # si solo cambió el estado a cancelada -> notificar cancelación
        if old_status != 'cancelled' and new_status == 'cancelled':
            _notify(instance, "Reserva cancelada")
            return

        # si cambio cualquier otro campo/estado -> notificar actualización
        _notify(instance, "Reserva actualizada")

    except Exception:
        logger.exception("Error en reservation_saved para reserva %s", getattr(instance, 'pk', '<no-id>'))


@receiver(post_delete, sender=Reservation)
def reservation_deleted(sender, instance, **kwargs):
    try:
        _notify(instance, "Reserva eliminada")
    except Exception:
        logger.exception("Error en reservation_deleted para reserva %s", getattr(instance, 'pk', '<no-id>'))
