from django.contrib import admin
from django.utils.html import format_html
from .models import Clinic, Specialization, Doctor, Schedule

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'phone')
    list_editable = ('is_active',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'address', 'phone', 'is_active')
        }),
    )

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'description')
        }),
    )

    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Tavsif'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'clinic', 'specialization', 'phone', 'experience_years', 'is_active')
    list_filter = ('clinic', 'specialization', 'is_active')
    search_fields = ('full_name', 'phone')
    list_editable = ('is_active',)
    raw_id_fields = ('user',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('user', 'full_name', 'phone', 'photo', 'bio', 'is_active')
        }),
        ('Mutaxassislik va tajriba', {
            'fields': ('specialization', 'experience_years')
        }),
        ('Shifoxona', {
            'fields': ('clinic',)
        }),
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_weekday_display', 'start_time', 'end_time', 'is_working')
    list_filter = ('weekday', 'is_working', 'doctor__clinic')
    search_fields = ('doctor__full_name',)
    list_editable = ('is_working',)
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('doctor', 'weekday', 'start_time', 'end_time', 'is_working')
        }),
    )
