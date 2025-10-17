from django.test import TestCase, RequestFactory
from reports.views import _get_daterange, _reservations_qs
from django.utils import timezone
from guest.models import Guest
from room.models import Room
from main.models import Reservation

class ReportsHelpersTests(TestCase):

    def test_get_daterange_defaults_and_custom(self):
        rf = RequestFactory()
        req = rf.get('/reports')  # sin params
        s, e = _get_daterange(req)
        self.assertIsNotNone(s)
        self.assertIsNotNone(e)

        req2 = rf.get('/reports', {'start': '2025-01-01', 'end': '2025-01-10'})
        s2, e2 = _get_daterange(req2)
        self.assertEqual(s2.isoformat(), "2025-01-01")
        self.assertEqual(e2.isoformat(), "2025-01-10")

    def test_reservations_qs_filters_by_dates(self):
        guest = Guest.objects.create(first_name="Anita", last_name="Burgos", email="a@gmail.com",
                                     phone_number="+57322546789", government_id="79845621", address="Cra 125 # 30 - 55")
        room = Room.objects.create(room_number="701", room_type="Sencilla", price_per_night=50)
        today = timezone.localdate()
        r1 = Reservation.objects.create(guest=guest, room=room, check_in_date=today, check_out_date=today, status='confirmed')
        qs = _reservations_qs(today, today)
        self.assertIn(r1, qs)

