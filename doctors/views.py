from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions
from django_filters import rest_framework as filters
from .models import Specialization, Doctor, Schedule
from .serializers import (
    SpecializationSerializer,
    DoctorListSerializer,
    DoctorDetailSerializer,
    ScheduleSerializer
)

# Template-based views
@login_required
def doctor_schedule(request):
    """View and manage doctor's schedule."""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar ish jadvalini ko\'rishi mumkin.')
        return redirect('home')

    doctor = request.user.doctor_profile
    
    if request.method == 'POST':
        # Get or create schedule for each weekday
        for weekday in range(7):
            is_working = request.POST.get(f'is_working_{weekday}', 'off') == 'on'
            start_time = request.POST.get(f'start_time_{weekday}', '')
            end_time = request.POST.get(f'end_time_{weekday}', '')
            
            if is_working and start_time and end_time:
                schedule, created = Schedule.objects.get_or_create(
                    doctor=doctor,
                    weekday=weekday,
                    defaults={
                        'start_time': start_time,
                        'end_time': end_time,
                        'is_working': True
                    }
                )
                
                if not created:
                    schedule.start_time = start_time
                    schedule.end_time = end_time
                    schedule.is_working = True
                    schedule.save()
            else:
                # If not working, mark as inactive
                Schedule.objects.filter(
                    doctor=doctor,
                    weekday=weekday
                ).update(is_working=False)
        
        messages.success(request, 'Ish jadvali muvaffaqiyatli saqlandi.')
        return redirect('doctors:schedule')
    
    # Get existing schedules
    schedules = Schedule.objects.filter(doctor=doctor)
    
    # Create default schedules for missing weekdays
    existing_weekdays = set(schedules.values_list('weekday', flat=True))
    for weekday in range(7):
        if weekday not in existing_weekdays:
            Schedule.objects.create(
                doctor=doctor,
                weekday=weekday,
                start_time='09:00',
                end_time='17:00',
                is_working=True
            )
    
    # Get all schedules again
    schedules = Schedule.objects.filter(doctor=doctor).order_by('weekday')
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'doctors/schedule.html', context)

# API views
class SpecializationListView(generics.ListAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.AllowAny]

class DoctorFilter(filters.FilterSet):
    clinic = filters.NumberFilter(field_name='clinic__id')
    specialization = filters.NumberFilter(field_name='specialization__id')

    class Meta:
        model = Doctor
        fields = ['clinic', 'specialization']

class DoctorListView(generics.ListAPIView):
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = DoctorFilter
    search_fields = ['full_name', 'specialization__name', 'clinic__name']

class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.filter(is_active=True)
    serializer_class = DoctorDetailSerializer
    permission_classes = [permissions.AllowAny]

class DoctorScheduleView(generics.ListAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Schedule.objects.filter(
            doctor_id=self.kwargs['pk'],
            is_working=True
        )
