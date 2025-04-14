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
from .forms import AppointmentForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
from datetime import datetime

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

def generate_appointment_pdf(appointment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Set colors
    title_color = (0.2, 0.4, 0.8)  # Dark blue
    header_color = (0.3, 0.6, 0.9)  # Light blue
    text_color = (0.1, 0.1, 0.1)  # Dark gray
    
    # Add header with color
    p.setFillColorRGB(*header_color)
    p.rect(0, 750, 600, 50, fill=1)
    
    # Add title with larger font
    p.setFont("Helvetica-Bold", 24)
    p.setFillColorRGB(1, 1, 1)  # White text
    p.drawString(100, 770, "NAVBAT CHIPTASI")
    
    # Reset font and color for content
    p.setFont("Helvetica-Bold", 16)
    p.setFillColorRGB(*title_color)
    
    # Add appointment number
    p.drawString(100, 700, f"Navbat raqami: #{appointment.queue_number}")
    
    # Add patient info
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(*text_color)
    p.drawString(100, 660, f"Bemor: {appointment.patient.full_name}")
    p.drawString(100, 630, f"Telefon: {appointment.patient.phone}")
    
    # Add doctor info
    p.setFont("Helvetica-Bold", 14)
    p.setFillColorRGB(*title_color)
    p.drawString(100, 590, "Doktor ma'lumotlari:")
    
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(*text_color)
    p.drawString(100, 560, f"Shifoxona: {appointment.doctor.clinic.name}")
    p.drawString(100, 530, f"Doktor: {appointment.doctor.full_name}")
    p.drawString(100, 500, f"Mutaxassislik: {appointment.doctor.specialization.name}")
    
    # Add appointment details
    p.setFont("Helvetica-Bold", 14)
    p.setFillColorRGB(*title_color)
    p.drawString(100, 460, "Navbat ma'lumotlari:")
    
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(*text_color)
    p.drawString(100, 430, f"Sana: {appointment.appointment_date.strftime('%d.%m.%Y')}")
    p.drawString(100, 400, f"Holat: {appointment.get_status_display()}")
    
    # Add notes if exists
    if appointment.notes:
        p.setFont("Helvetica-Bold", 14)
        p.setFillColorRGB(*title_color)
        p.drawString(100, 370, "Qo'shimcha ma'lumotlar:")
        
        p.setFont("Helvetica", 14)
        p.setFillColorRGB(*text_color)
        p.drawString(100, 340, appointment.notes)
    
    # Add footer
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.5, 0.5, 0.5)  # Gray
    p.drawString(100, 50, "Bu chipta elektron tarzda yaratilgan va qonuniy kuchga ega.")
    
    p.save()
    buffer.seek(0)
    return buffer

def appointment_create(request, doctor_id):
    """View for creating a new appointment with a specific doctor"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, doctor=doctor)
        if form.is_valid():
            try:
                # Try to get existing patient by phone
                patient = Patient.objects.get(phone=form.cleaned_data['phone'])
                # Update patient's name if it's different
                if patient.full_name != form.cleaned_data['full_name']:
                    patient.full_name = form.cleaned_data['full_name']
                    patient.save()
            except Patient.DoesNotExist:
                # Generate a unique telegram_id for web appointments
                web_id = f"web_{int(timezone.now().timestamp())}"
                # Create new patient if doesn't exist
                patient = Patient.objects.create(
                    phone=form.cleaned_data['phone'],
                    full_name=form.cleaned_data['full_name'],
                    telegram_id=web_id
                )
            
            # Convert string date to date object
            appointment_date = datetime.strptime(form.cleaned_data['appointment_date'], '%Y-%m-%d').date()
            
            # Get the last appointment for this doctor and date
            last_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date
            ).order_by('-queue_number').first()
            
            # Calculate next queue number
            next_queue_number = 1 if not last_appointment else last_appointment.queue_number + 1
            
            # Create appointment
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                appointment_date=appointment_date,
                notes=form.cleaned_data['reason'],
                status='pending',
                queue_number=next_queue_number
            )
            
            # Generate PDF
            pdf_buffer = generate_appointment_pdf(appointment)
            
            # Create response with patient name in filename
            safe_filename = patient.full_name.replace(' ', '_')
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="navbat_{safe_filename}.pdf"'
            
            # Add success message with extra_tags for timing
            messages.success(request, f"Navbat muvaffaqiyatli olindi! Navbat raqami: {appointment.queue_number}", extra_tags='timeout=10000')
            
            # Return PDF response
            return response
    else:
        form = AppointmentForm(doctor=doctor)
    
    return render(request, 'appointments/appointment_create.html', {
        'form': form,
        'doctor': doctor
    })

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
