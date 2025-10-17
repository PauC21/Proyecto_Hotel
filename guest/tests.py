from django.test import TestCase
from django.core.exceptions import ValidationError
from guest.forms import GuestForm
from guest.models import Guest

class GuestFormAndModelTests(TestCase):

    def test_clean_government_id_rejects_duplicate_on_create(self):
        # Arrange: guest existente
        Guest.objects.create(first_name="Juan", last_name="Perez", email="juan@gmail.com",
                             phone_number="+573001112233", government_id="123456789", address="Calle 1 # 47 f 18")
        data = {
            "first_name": "Ana",
            "last_name": "Lopez",
            "email": "ana@gmail.com",
            "phone_number": "+573009998877",
            "government_id": "123456789",  # duplicado
            "address": "Calle 2 # 54 a 10"
        }
        form = GuestForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('government_id', form.errors)
        self.assertTrue(any("Ya existe" in e for e in form.errors['government_id']))

    def test_clean_government_id_allows_same_value_on_edit(self):
        # Arrange: crear guest y editar con el mismo government_id
        g = Guest.objects.create(first_name="Lucia", last_name="Martinez", email="lucia@gmail.com",
                                 phone_number="+573208132589", government_id="987654321", address="cra 6 # 15 e 13")
        data = {
            "first_name": g.first_name,
            "last_name": g.last_name,
            "email": g.email,
            "phone_number": g.phone_number,
            "government_id": g.government_id,
            "address": g.address,
        }
        form = GuestForm(data=data, instance=g)
        self.assertTrue(form.is_valid())

    def test_guest_str_and_get_absolute_url(self):
        g = Guest.objects.create(first_name="Pablo", last_name="Irlanda", email="p@gmail.com",
                                 phone_number="+573158745963", government_id="53789641", address="av 26 calle 300 a 6")
        s = str(g)
        self.assertIn("Pablo", s)
        self.assertIn("53789641", s)
        url = g.get_absolute_url()
        self.assertIsInstance(url, str)

