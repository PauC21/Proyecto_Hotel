# notifications/utils.py
import logging
from django.conf import settings
from django.core.mail import send_mail
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from django.utils.timezone import now


# Twilio
from twilio.rest import Client

logger = logging.getLogger(__name__)

def notify_email(to_email: str, subject: str, message: str):
    if not to_email:
        logger.debug("notify_email: destino vacío, omitiendo.")
        return
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
        logger.info(f"Email enviado a {to_email}: {subject}")
    except Exception as e:
        logger.exception(f"Error enviando email a {to_email}: {e}")

def _twilio_client()->Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def notify_whatsapp(to_number: str, message: str) -> bool:
    """
    Envía mensaje por WhatsApp usando el sandbox de Twilio.
    Requiere que el destinatario haya 'join' el sandbox y tenga ventana activa.
    """
    try:
        if not to_number.startswith("+"):
            raise ValueError("Número debe estar en formato E.164, ej: +57310XXXXXXX")

        client = _twilio_client()
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,   # "whatsapp:+14155238886"
            to=f"whatsapp:{to_number}"              # "whatsapp:+57310XXXXXXX"
        )
        return True
    except Exception as e:
        print(f"Error enviando WhatsApp a {to_number}: {e}")
        return False

def notify_sms(to_number: str, message: str, *, fallback_to_whatsapp: bool = True) -> bool:
    """
    Intenta SMS; si falla (trial, A2P, etc.), opcionalmente hace fallback a WhatsApp.
    """
    try:
        if not to_number.startswith("+"):
            raise ValueError("Número debe estar en formato E.164, ej: +57310XXXXXXX")

        # Acotar para SMS si quieres (1600 máx suele estar OK)
        short_msg = message if len(message) <= 1600 else message[:1597] + "..."

        client = _twilio_client()
        client.messages.create(
            body=short_msg,
            from_=settings.TWILIO_PHONE_NUMBER,  # tu número Twilio
            to=to_number
        )
        return True

    except TwilioRestException as e:
        # Errores habituales (trial, número no verificado, país bloqueado, etc.)
        print(f"Error enviando SMS a {to_number}: {e}")
        if fallback_to_whatsapp:
            print("Reintentando por WhatsApp (fallback)…")
            return notify_whatsapp(to_number, message)
        return False

    except Exception as e:
        print(f"Error general enviando SMS a {to_number}: {e}")
        if fallback_to_whatsapp:
            print("Reintentando por WhatsApp (fallback)…")
            return notify_whatsapp(to_number, message)
        return False