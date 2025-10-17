from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import Reservation
from django.views.generic import DetailView
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from room.models import Room
from guest.models import Guest
from django.views.generic import DeleteView
from django.contrib import messages
from notifications import send_email, send_sms
from notifications.utils import notify_email, notify_sms, notify_whatsapp
from django.utils.timezone import now
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from room.forms import CustomReservationForm


class Moddview(View):
    def get(self,request):
        return render(request,'modd.html')

class DashboardView(View):
    def get(self, request):
        total_rooms = Room.objects.all().count()
        total_guests = Guest.objects.all().count()
        total_reservations = Reservation.objects.all().count()
        context = {
            'total_rooms': total_rooms,
            'total_guests': total_guests,
            'total_reservations': total_reservations,
        }
        return render(request, 'dashboard.html', context)

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    template_name = "reservation_form.html"
    form_class = CustomReservationForm
    success_url = reverse_lazy("reservation_list")

    def get_initial(self):
        initial = super().get_initial()
        guest_id = self.request.GET.get('guest_id')
        if guest_id:
            initial['guest'] = guest_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Reservation"
        return context

    def form_valid(self, form):
        # obtener datos del formulario
        room = form.cleaned_data['room']
        check_in_date = form.cleaned_data['check_in_date']
        check_out_date = form.cleaned_data['check_out_date']

        # 1) bloquear si la habitación está en mantenimiento
        if getattr(room, "status", None) == "maintenance":
            form.add_error('room', 'Esta habitación está en mantenimiento y no se puede reservar.')
            return self.form_invalid(form)

        # 2) validación de solapamiento de reservas
        existing_reservations = Reservation.objects.filter(
        room=room,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
        ).exclude(status='cancelled')

        if existing_reservations.exists():
            form.add_error('room', 'This room is already booked for the selected dates.')
            return self.form_invalid(form)

        # 3) guardar la reserva (CreateView ya la guarda en super().form_valid)
        response = super().form_valid(form)

        # 4) mensaje al usuario
        messages.success(self.request, "La reserva fue creada y se notificó al cliente.")

        # 5) devolver la respuesta ya generada por super()
        return response

class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    template_name = "reservation_form.html"
    form_class = CustomReservationForm
    success_url = reverse_lazy("reservation_list")

    def dispatch(self, request, *args, **kwargs):
        """Evita editar reservas canceladas."""
        self.object = self.get_object()
        if self.object.status == 'cancelled':
            messages.error(request, "No se puede editar una reserva cancelada.")
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Update Reservation"
        return context
    
    def form_valid(self, form):
        room = form.cleaned_data['room']
        check_in_date = form.cleaned_data['check_in_date']
        check_out_date = form.cleaned_data['check_out_date']

        # excluir la reserva actual para que no choque consigo misma
        existing_reservations = Reservation.objects.filter(
        room=room,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date
        ).exclude(pk=self.object.pk).exclude(status='cancelled')

        if existing_reservations.exists():
            form.add_error('room', 'This room is already booked for the selected dates.')
            return self.form_invalid(form)
        else:
            response = super().form_valid(form)
        
        messages.success(self.request, "La reserva fue actualizada y se notificó al cliente.")
        return super().form_valid(form)

class ReservationDeleteView(DeleteView):
    model = Reservation
    template_name = "reservation_confirm_delete.html"  # archivo en main/templates/
    context_object_name = "reservation"
    success_url = reverse_lazy("reservation_list")

    # Para mostrar un mensaje al eliminar
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reservation"] = self.object
        return context
    
    def delete(self, request, *args, **kwargs):
        reservation = self.get_object()
        guest = reservation.guest

        messages.success(self.request, "La reserva fue eliminada y se notificó al cliente.")
        return super().delete(request, *args, **kwargs)
    


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = "reservation_detail.html"

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    paginate_by = 10
    context_object_name = "reservations"
    template_name = "reservation_list.html"
    def get_queryset(self):
        # Get the room number from the query parameters
        room_number = self.request.GET.get('room_number')

        # Filter reservations for the specified room number
        if room_number:
            return Reservation.objects.filter(room__room_number=int(room_number)).order_by('-id')
        else:
            return Reservation.objects.all().order_by('-id')
        
class ReservationCancelView(LoginRequiredMixin, View):
    """Marca una reserva como 'cancelled' (NO la elimina)."""
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)

        # si ya está cancelada, no hacer nada
        if reservation.status == 'cancelled':
            messages.info(request, "La reserva ya está cancelada.")
            return redirect(reservation.get_absolute_url() if hasattr(reservation, 'get_absolute_url') else reverse_lazy('reservation_detail', kwargs={'pk': pk}))

        # marcar como cancelada
        reservation.status = 'cancelled'
        reservation.save()

        # Si la habitación estaba marcada ocupada explícitamente, liberarla.
        try:
            room = reservation.room
            # fecha actual (usamos date porque normalmente check_in_date/check_out_date son DateField)
            now = timezone.now()
            today = now.date()

            # buscamos otras reservas *activas* (NO canceladas) para esta habitación
            # que cubran la fecha actual. Excluimos la reserva que acabamos de cancelar por seguridad.
            other_active = room.reservation_set.exclude(status='cancelled') \
                .exclude(pk=reservation.pk) \
                .filter(check_in_date__lte=today, check_out_date__gte=today) \
                .exists()

            # Si no hay otra reserva activa, liberamos la habitación
            if not other_active:
                if hasattr(room, 'status') and room.status != 'available':
                    room.status = 'available'
                    room.save()
        except Exception as e:
            # No romper la operación por un fallo en la lógica de recálculo;
            # registramos el error para depuración.
            import logging
            logging.getLogger(__name__).exception("Error recalculando estado de la habitación al cancelar: %s", e)


        messages.success(request, "Reserva cancelada correctamente. Quedará en el historial.")
        return redirect(reverse_lazy('reservation_detail', kwargs={'pk': pk}))
        

@login_required
def toggle_maintenance(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if room.status == 'maintenance':
        room.status = 'available'
        messages.success(request, f"La habitación {room.room_number} ha sido marcada como disponible.")
    else:
        room.status = 'maintenance'
        messages.warning(request, f"La habitación {room.room_number} ha sido puesta en mantenimiento.")
    room.save()
    return redirect(reverse('room_detail', kwargs={'pk': pk}))