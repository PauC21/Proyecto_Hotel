from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Guest
from .forms import GuestForm
from django.views.generic import CreateView,ListView,DetailView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from main.models import Reservation
from django.core.paginator import Paginator


class GuestCreateView(LoginRequiredMixin, CreateView):
    model = Guest
    template_name = "guest_form.html"   # un solo template compartido
    fields = "__all__"

    #  corregimos el contexto
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)  # heredamos el contexto padre
        ctx["guest"] = None                       # importante para distinguir en el form
        ctx["mode"] = "create"
        ctx["title"] = "Crear huésped"   
        return ctx

    #  Después de crear un guest, redirige al detalle
    def get_success_url(self):
        return reverse("guest_detail", args=[self.object.pk])
    

class GuestListView(LoginRequiredMixin, ListView):
    model = Guest
    context_object_name = "guests"
    paginate_by = 10
    template_name = "guest_list.html"
    def get_queryset(self):
        return Guest.objects.all().order_by('-id')

class GuestDetailView(DetailView):
    model = Guest
    template_name = "guest_detail.html"
    context_object_name = "guest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guest = self.object

        # todas las reservas del huésped, ordenadas por check_in_date descendente
        reservations_qs = Reservation.objects.filter(guest=guest).order_by('-check_in_date', '-pk')

        # opcional: paginar el historial si hay muchas reservas
        paginator = Paginator(reservations_qs, 10)  # 10 por página
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['reservations'] = page_obj.object_list
        context['reservations_page_obj'] = page_obj
        return context


#Modificar huésped
def guest_update(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == "POST":
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            messages.success(request, "Huésped actualizado correctamente.")
            return redirect("guest_detail", pk=guest.pk)
    else:
        form = GuestForm(instance=guest)
    return render(request, "guest_form.html", {"form": form, "guest": guest, "title": "Editar Huesped"})


# Eliminar huésped
def guest_delete(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == "POST":
        guest.delete()
        messages.success(request, "Huésped eliminado correctamente.")
        return redirect("guest_list")
    # GET: mostrar confirmación
    return render(request, "guest_confirm_delete.html", {"guest": guest})