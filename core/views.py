from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.contrib.auth.models import User
from doctors.models import Doctor, Clinic, Specialization
from appointments.models import Appointment, Patient
from django.utils import timezone
from core.models import ClinicRoom
from django.http import HttpResponseNotFound

def is_admin(user):
    return user.is_superuser

def home(request):
    """Main page view - shows hospital information"""
    # Get statistics
    total_rooms = ClinicRoom.objects.count()
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Get average experience of doctors
    doctors = Doctor.objects.filter(years_of_experience__gt=0)
    total_experience = sum(doctor.years_of_experience for doctor in doctors)
    avg_experience = total_experience / len(doctors) if len(doctors) > 0 else 0
    
    context = {
        'total_rooms': total_rooms,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'avg_experience': round(avg_experience, 1)
    }
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin-dashboard')
        elif hasattr(request.user, 'doctor_profile'):
            return redirect('dashboard')
    return render(request, 'core/home.html', context)

class CustomLoginView(LoginView):
    """Custom login view to handle redirects"""
    template_name = 'core/login.html'
    
    def get_success_url(self):
        # Check if there's a next parameter
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # Redirect to appropriate dashboard based on user type
        if self.request.user.is_superuser:
            return '/admin-dashboard/'
        elif hasattr(self.request.user, 'doctor_profile'):
            return '/dashboard/'
        return '/'

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        messages.success(self.request, 'Siz tizimdan chiqdingiz')
        return '/'

@login_required
def dashboard(request):
    """Dashboard view for logged in doctors"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Siz shifokor emassiz. Faqat shifokorlar dashboardni ko\'rishi mumkin.')
        return redirect('home')

    doctor = request.user.doctor_profile
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('queue_number')

    context = {
        'appointments': appointments,
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get statistics
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    total_clinics = Clinic.objects.count()
    total_specializations = Specialization.objects.count()
    
    # Get all doctors for filters
    doctors = Doctor.objects.all()
    
    # Get filtered appointments
    appointments = Appointment.objects.select_related('doctor', 'patient')
    
    # Apply filters
    date_filter = request.GET.get('date')
    status_filter = request.GET.get('status')
    doctor_filter = request.GET.get('doctor')
    queue_filter = request.GET.get('queue')
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            appointments = appointments.filter(appointment_date=today)
        elif date_filter == 'tomorrow':
            tomorrow = today + timezone.timedelta(days=1)
            appointments = appointments.filter(appointment_date=tomorrow)
        elif date_filter == 'next_7_days':
            next_week = today + timezone.timedelta(days=7)
            appointments = appointments.filter(appointment_date__range=[today, next_week])
        elif date_filter == 'next_30_days':
            next_month = today + timezone.timedelta(days=30)
            appointments = appointments.filter(appointment_date__range=[today, next_month])
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    
    # Apply queue filter
    if queue_filter == 'start':
        appointments = appointments.order_by('queue_number')
    elif queue_filter == 'end':
        appointments = appointments.order_by('-queue_number')
    else:
        appointments = appointments.order_by('-created_at')
    
    # Get recent appointments (filtered or not)
    recent_appointments = appointments[:10]
    
    # Get recent doctors
    recent_doctors = Doctor.objects.select_related(
        'clinic', 'specialization'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_clinics': total_clinics,
        'total_specializations': total_specializations,
        'recent_appointments': recent_appointments,
        'recent_doctors': recent_doctors,
        'doctors': doctors,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def profile(request):
    """User profile view"""
    doctor = getattr(request.user, 'doctor_profile', None)
    is_doctor = doctor is not None
    
    if is_doctor:
        # Get all appointments for the doctor
        appointments = Appointment.objects.filter(
            doctor=doctor
        ).order_by('-appointment_date', 'queue_number')
    else:
        appointments = None

    context = {
        'doctor': doctor,
        'is_doctor': is_doctor,
        'appointments': appointments,
    }
    return render(request, 'core/profile.html', context)

def doctors_list(request):
    """View to display list of all doctors"""
    doctors = Doctor.objects.all()
    return render(request, 'core/doctors.html', {'doctors': doctors})

def doctor_detail(request, doctor_id):
    """View to display detailed information about a specific doctor"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'core/doctor_detail.html', {'doctor': doctor})

def handler404(request, exception):
    return render(request, '404.html', status=404)
