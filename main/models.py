from django.db import models
from django.urls import reverse


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente de confirmación"),
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
        ("check_in", "Registrado / Check-in"),
        ("check_out", "Finalizado / Check-out"),
    ]
    room = models.ForeignKey('room.Room', on_delete=models.CASCADE)
    guest = models.ForeignKey('guest.Guest', on_delete=models.CASCADE)
    additional = models.TextField(null=True,blank=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    def get_absolute_url(self):
        return reverse('reservation_detail', args=[str(self.id)])
    def __str__(self):
        return f"Reserva {self.pk} - {self.guest} - {self.room} ({self.get_status_display()})"

