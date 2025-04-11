from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, ChoiceFilter
from .models import Appointment, Patient
from .serializers import (
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentCreateSerializer,
    AppointmentCancelSerializer,
    PatientSerializer,
    AppointmentSerializer
)
from doctors.models import Doctor
from .permissions import IsDoctor

# Create your views here.

class AppointmentFilter:
    def __init__(self, queryset, request):
        self.queryset = queryset
        self.request = request

    def filter(self):
        date = self.request.query_params.get('date', None)
        status = self.request.query_params.get('status', None)
        
        if date:
            self.queryset = self.queryset.filter(appointment_date=date)
        
        if status and status != 'all':
            self.queryset = self.queryset.filter(status=status)
        
        return self.queryset.order_by('queue_number')

# Template-based views
@login_required
def appointment_list(request):
    """List appointments for the logged-in doctor."""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar navbatlarni ko\'rishi mumkin.')
        return redirect('home')

    doctor = request.user.doctor_profile
    status = request.GET.get('status', None)
    today = request.GET.get('today', None)
    
    # Get appointments for the doctor
    appointments = Appointment.objects.filter(doctor=doctor)
    
    # Filter by today's date if today parameter is present
    if today:
        today_date = timezone.now().date()
        appointments = appointments.filter(appointment_date=today_date)
    
    # Filter by status if provided
    if status and status != 'all':
        appointments = appointments.filter(status=status)
    
    # Order by date and queue number
    appointments = appointments.order_by('-appointment_date', 'queue_number')

    context = {
        'appointments': appointments,
        'is_today': bool(today),
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def doctor_appointment_list(request):
    """List appointments for the logged-in doctor with additional actions."""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar navbatlarni ko\'rishi mumkin.')
        return redirect('home')

    doctor = request.user.doctor_profile
    status = request.GET.get('status', None)
    today = request.GET.get('today', None)
    
    # Get appointments for the doctor
    appointments = Appointment.objects.filter(doctor=doctor)
    
    # Filter by today's date if today parameter is present
    if today:
        today_date = timezone.now().date()
        appointments = appointments.filter(appointment_date=today_date)
    
    # Filter by status if provided
    if status and status != 'all':
        appointments = appointments.filter(status=status)
    
    # Order by date and queue number
    appointments = appointments.order_by('-appointment_date', 'queue_number')

    context = {
        'appointments': appointments,
        'is_today': bool(today),
    }
    return render(request, 'appointments/doctor_appointment_list.html', context)

@login_required
def appointment_detail(request, pk):
    """View details of a specific appointment."""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar navbatlarni ko\'rishi mumkin.')
        return redirect('home')

    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.doctor != request.user.doctor_profile:
        messages.error(request, 'Bu navbat sizga tegishli emas.')
        return redirect('appointments:appointment-list')

    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def appointment_cancel(request, pk):
    """Cancel a specific appointment."""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar navbatlarni bekor qilishi mumkin.')
        return redirect('home')

    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.doctor != request.user.doctor_profile:
        messages.error(request, 'Bu navbat sizga tegishli emas.')
        return redirect('appointments:appointment-list')

    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        
        if action == 'confirm':
            if appointment.confirm():
                messages.success(request, 'Navbat muvaffaqiyatli tasdiqlandi.')
            else:
                messages.error(request, 'Navbatni tasdiqlab bo\'lmaydi.')
        elif action == 'complete':
            if appointment.complete():
                messages.success(request, 'Navbat muvaffaqiyatli bajarildi deb belgilandi.')
            else:
                messages.error(request, 'Navbatni bajarildi deb belgilab bo\'lmaydi.')
        elif action == 'cancel':
            if appointment.cancel(reason=reason):
                messages.success(request, 'Navbat muvaffaqiyatli bekor qilindi.')
            else:
                messages.error(request, 'Navbatni bekor qilib bo\'lmaydi.')
        
        return redirect('appointments:doctor-appointment-list')

    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_cancel.html', context)

# API views
class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    filterset_class = AppointmentFilter

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user.doctor_profile)

class AppointmentDetailView(generics.RetrieveAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'doctor_profile'):
            return Appointment.objects.filter(doctor=self.request.user.doctor_profile)
        return Appointment.objects.none()

class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get or create patient from user
        patient, _ = Patient.objects.get_or_create(
            telegram_id=self.request.user.username,
            defaults={
                'full_name': self.request.user.get_full_name(),
                'phone': ''  # This should be set through the Telegram bot
            }
        )
        serializer.save(patient=patient)

class AppointmentCancelView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCancelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'doctor_profile'):
            return Appointment.objects.filter(doctor=self.request.user.doctor_profile)
        return Appointment.objects.none()

class MyAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AppointmentFilter

    def get_queryset(self):
        return Appointment.objects.filter(
            patient__telegram_id=self.request.user.username
        )

class AppointmentViewSet(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AppointmentFilter

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user.doctor)

    @action(detail=False, methods=['get'])
    def my_appointments(self, request):
        appointments = self.get_queryset()
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's appointments."""
        appointments = self.get_queryset().filter(
            appointment_date=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('queue_number')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming appointments."""
        appointments = self.get_queryset().filter(
            appointment_date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date', 'queue_number')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        if appointment.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed appointments can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.cancellation_reason = request.data.get('reason', '')
        appointment.save()
        
        return Response({'status': 'Appointment cancelled'})
