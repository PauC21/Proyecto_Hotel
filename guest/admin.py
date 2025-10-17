from django.contrib import admin
from .models import Guest

admin.site.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "phone_number")
    search_fields = ("first_name", "last_name", "email", "phone_number")
