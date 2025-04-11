from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, Appointment, Queue

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'telegram_id', 'is_blocked', 'created_at')
    list_filter = ('is_blocked',)
    search_fields = ('full_name', 'phone', 'telegram_id')
    list_editable = ('is_blocked',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('full_name', 'phone', 'telegram_id', 'is_blocked')
        }),
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'queue_number', 'status', 'created_at')
    list_filter = ('status', 'doctor__clinic', 'appointment_date')
    search_fields = ('patient__full_name', 'patient__phone', 'doctor__full_name')
    list_editable = ('status',)
    raw_id_fields = ('patient', 'doctor')
    date_hierarchy = 'appointment_date'
    ordering = ('-appointment_date', 'queue_number')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('patient', 'doctor', 'appointment_date', 'queue_number', 'status')
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('notes', 'cancellation_reason')
        }),
    )
    
    def status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'cancelled': 'danger',
            'completed': 'info'
        }
        status_names = {
            'pending': 'Kutilmoqda',
            'confirmed': 'Tasdiqlangan',
            'cancelled': 'Bekor qilingan',
            'completed': 'Yakunlangan'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            status_colors.get(obj.status, 'secondary'),
            status_names.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Holati'

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'current_number', 'last_number', 'is_active')
    list_filter = ('is_active', 'date', 'doctor__clinic')
    search_fields = ('doctor__full_name',)
    list_editable = ('is_active',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('doctor', 'date', 'current_number', 'last_number', 'is_active')
        }),
    )
