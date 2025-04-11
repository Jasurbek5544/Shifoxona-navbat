from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.models import Doctor, Patient, Appointment
from doctors.models import Specialization, Clinic, Schedule
from datetime import timedelta, time
import random

class Command(BaseCommand):
    help = 'Creates test data for the application'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Schedule.objects.all().delete()
        Doctor.objects.all().delete()
        Specialization.objects.all().delete()
        Clinic.objects.all().delete()
        get_user_model().objects.filter(is_superuser=False).delete()
        self.stdout.write('Cleared existing data')

        # Create specializations
        specializations = [
            'Terapevt',
            'Kardiolog',
            'Nevrolog',
            'Pediatr',
            'Stomatolog',
            'Oftalmolog',
            'Endokrinolog',
            'Ginekolog',
            'Urolog',
            'Ortoped'
        ]
        
        for spec in specializations:
            Specialization.objects.get_or_create(name=spec)
            self.stdout.write(self.style.SUCCESS(f'Created specialization: {spec}'))

        # Create clinics
        clinics = [
            'Toshkent Tibbiyot Akademiyasi',
            'Toshkent Shahar Klinik Shifoxonasi',
            'Respublika Kardiologiya Markazi',
            'Toshkent Pediatriya Instituti',
            'Respublika Onkologiya Markazi'
        ]
        
        for clinic in clinics:
            Clinic.objects.get_or_create(name=clinic)
            self.stdout.write(self.style.SUCCESS(f'Created clinic: {clinic}'))

        # Create doctors
        doctors = [
            {'name': 'Alisher Aliyev', 'specialization': 'Terapevt'},
            {'name': 'Dilfuza Karimova', 'specialization': 'Kardiolog'},
            {'name': 'Shavkat Rahimov', 'specialization': 'Nevrolog'},
            {'name': 'Zulfiya Yusupova', 'specialization': 'Pediatr'},
            {'name': 'Jamshid Ismoilov', 'specialization': 'Stomatolog'},
            {'name': 'Malika Abdullayeva', 'specialization': 'Oftalmolog'},
            {'name': 'Rustam Tursunov', 'specialization': 'Endokrinolog'},
            {'name': 'Gulnora Mirzayeva', 'specialization': 'Ginekolog'},
            {'name': 'Farhod Usmonov', 'specialization': 'Urolog'},
            {'name': 'Dilbar Rahimova', 'specialization': 'Ortoped'}
        ]
        
        # Working hours variants
        working_hours = [
            {'start': '09:00', 'end': '18:00'},  # Standard full day
            {'start': '08:00', 'end': '16:00'},  # Early shift
            {'start': '10:00', 'end': '19:00'},  # Late shift
            {'start': '09:00', 'end': '15:00'},  # Half day
            {'start': '14:00', 'end': '22:00'},  # Evening shift
        ]
        
        for doctor_data in doctors:
            specialization = Specialization.objects.get(name=doctor_data['specialization'])
            clinic = Clinic.objects.order_by('?').first()
            
            # Create user for doctor
            username = doctor_data['name'].lower().replace(' ', '_')
            user = get_user_model().objects.create_user(
                username=username,
                password='testpass123',
                first_name=doctor_data['name'].split()[0],
                last_name=doctor_data['name'].split()[1]
            )
            
            doctor, created = Doctor.objects.get_or_create(
                user=user,
                full_name=doctor_data['name'],
                specialization=specialization,
                clinic=clinic,
                defaults={
                    'phone': f'+9989{random.randint(10000000, 99999999)}',
                    'experience_years': random.randint(1, 30),
                    'bio': f"{doctor_data['name']} - {specialization.name} mutaxassisi",
                    'is_active': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created doctor: {doctor_data["name"]}'))

            # Create schedule for each doctor
            # Each doctor works 5-6 days a week with random working hours
            working_days = random.sample(range(7), random.randint(5, 6))  # 5-6 random days
            work_hours = random.choice(working_hours)
            
            for day in working_days:
                Schedule.objects.get_or_create(
                    doctor=doctor,
                    weekday=day,
                    defaults={
                        'start_time': work_hours['start'],
                        'end_time': work_hours['end'],
                        'is_working': True
                    }
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Created schedule for {doctor.full_name} on day {day} '
                    f'({work_hours["start"]} - {work_hours["end"]})'
                ))

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 