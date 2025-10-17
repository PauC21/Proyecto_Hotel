# guest/models.py
from django.db import models
from django.urls import reverse

class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True,null=True,help_text="Número en formato internacional, ej: +573001112233")
    government_id = models.CharField(max_length=15, unique=True)
    address = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.government_id})"
    

    def get_absolute_url(self):
        # Esto asegura que Django siempre pueda redirigir al detalle del huésped recién creado
        return reverse('guest_detail', args=[str(self.id)])