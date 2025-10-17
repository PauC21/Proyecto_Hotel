from django.test import TestCase
from django.utils import timezone
from datetime import date, datetime, time as dtime, timedelta
from django.utils.timezone import is_aware
from room.models import Room
from main.models import Reservation
from guest.models import Guest
from room.forms import CustomReservationForm


class RoomModelTests(TestCase):

    def test_is_under_maintenance_property(self):
        r = Room.objects.create(room_number="101", room_type="Doble", price_per_night=100, status="maintenance")
        self.assertTrue(r.is_under_maintenance)
        r.status = "available"
        r.save()
        self.assertFalse(r.is_under_maintenance)

    def test_as_datetime_with_date_and_naive_datetime(self):
        r = Room.objects.create(room_number="102", room_type="Sencilla", price_per_night=80)
        d = date(2025, 10, 10)
        dt = r._as_datetime(d)
        self.assertTrue(is_aware(dt))
        self.assertEqual(dt.date(), d)

        naive = datetime(2025, 10, 11, 9, 0, 0)
        dt2 = r._as_datetime(naive)
        self.assertTrue(is_aware(dt2))

    def test_is_booked_now_true_and_false(self):
        guest = Guest.objects.create(first_name="Gio", last_name="Meneces", email="g@gmial.com",
                                     phone_number="+573185796323", government_id="237984251", address="calle 100 # 45 - 10")
        r = Room.objects.create(room_number="200", room_type="Suite", price_per_night=200, status="occupied")
        today = timezone.localdate()
        # reserva que cubre hoy
        res = Reservation.objects.create(room=r, guest=guest, check_in_date=today - timedelta(days=1),
                                         check_out_date=today + timedelta(days=1), status='confirmed')
        self.assertTrue(r.is_booked_now)
        # cancelar -> debería dejar de aparecer
        res.status = 'cancelled'
        res.save()
        # refrescar instancia del room por si acaso
        r.refresh_from_db()
        self.assertFalse(r.is_booked_now)

    def test_clean_rejects_past_checkin_and_checkout_not_after_checkin(self):
        guest = Guest.objects.create(first_name="Mariana", last_name="Bonilla", email="mar2111@gmail.com",
                                     phone_number="+57310247856", government_id="53798412", address="avenida caracas 20 #39 - 60")
        room = Room.objects.create(room_number="301", room_type="Doble", price_per_night=100)
        today = timezone.localdate()
        past = today - timedelta(days=1)

        data = {
            "guest": guest.id,
            "room": room.id,
            "check_in_date": past.isoformat(),
            "check_out_date": (today + timedelta(days=1)).isoformat(),
        }
        form = CustomReservationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('check_in_date', form.errors)

        # checkout <= checkin
        data2 = {
            "guest": guest.id,
            "room": room.id,
            "check_in_date": (today + timedelta(days=2)).isoformat(),
            "check_out_date": (today + timedelta(days=2)).isoformat(),
        }
        form2 = CustomReservationForm(data=data2)
        self.assertFalse(form2.is_valid())
        self.assertIn('check_out_date', form2.errors)

