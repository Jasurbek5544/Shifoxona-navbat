from django.contrib import admin
from .models import TimeStampedModel, ClinicRoom

# Clinic model registration removed as it's already registered in doctors/admin.py

@admin.register(ClinicRoom)
class ClinicRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_number', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('name', 'room_number')
