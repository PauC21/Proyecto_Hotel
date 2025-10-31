from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView,ListView
from .models import Room
from .forms import RoomForm
from django.urls import reverse_lazy
from main.models import Reservation
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    template_name = "room_form.html"
    fields = "__all__"
    success_url = reverse_lazy('room_list')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Crear habitación"
        return ctx
    

class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    context_object_name = "rooms"
    paginate_by = 10
    template_name = "room_list.html"

class RoomDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        current_datetime = timezone.now()
        today = current_datetime.date()
        reservations = room.reservation_set.exclude(status='cancelled') \
            .filter(check_out_date__gte=today) \
            .order_by('check_in_date')        
        return render(request, 'room_detail.html', {'room': room, 'reservations': reservations,})

#opcion "modificar" habitación
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("room_detail", pk=room.pk)
    else:
        form = RoomForm(instance=room)
    return render(request, "room_form.html", {"form": form, "room": room, "title": "Editar habitación"})


#opcion "eliminar" habitación
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        room.delete()
        return redirect("room_list")
    return render(request, "room/room_confirm_delete.html", {"room": room})

