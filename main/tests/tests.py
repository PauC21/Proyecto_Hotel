from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from guest.models import Guest
from room.models import Room
from main.models import Reservation

class ReservationOverlapTests(TestCase):

    def test_overlap_detection_query_returns_existing_on_overlap(self):
        guest = Guest.objects.create(first_name="JOse", last_name="Bustos", email="joseb@gmail.com",
                                     phone_number="+57312456789", government_id="637456332", address="Casa 10 via siberia")
        room = Room.objects.create(room_number="801", room_type="Tiple", price_per_night=60)
        start = timezone.localdate()
        end = start + timedelta(days=2)
        # existing reservation overlapping (start +1 .. end+1)
        Reservation.objects.create(guest=guest, room=room, check_in_date=start + timedelta(days=1),
                                   check_out_date=end + timedelta(days=1), status='confirmed')
        # simulate filter used in view
        existing = Reservation.objects.filter(
            room=room,
            check_in_date__lt=end,
            check_out_date__gt=start
        ).exclude(status='cancelled')
        self.assertTrue(existing.exists())

    def test_overlap_detection_query_returns_none_when_no_overlap(self):
        guest = Guest.objects.create(first_name="Carlos", last_name="Diaz", email="cd@hotmail.com",
                                     phone_number="+57313896412", government_id="14526897", address="Calle 100 # 30 -12")
        room = Room.objects.create(room_number="802", room_type="VIP", price_per_night=60)
        # existing reservation well before
        Reservation.objects.create(guest=guest, room=room,
                                   check_in_date=timezone.localdate() - timedelta(days=10),
                                   check_out_date=timezone.localdate() - timedelta(days=8),
                                   status='confirmed')
        start = timezone.localdate()
        end = start + timedelta(days=2)
        existing = Reservation.objects.filter(
            room=room,
            check_in_date__lt=end,
            check_out_date__gt=start
        ).exclude(status='cancelled')
        self.assertFalse(existing.exists())

