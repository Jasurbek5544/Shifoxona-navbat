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
            'Ortoped',
            'Dermatolog',
            'Onkolog',
            'Reanimatolog',
            'Nefrolog',
            'Travmatolog',
            'LOR (Otolarinolog)',
            'Pulmonolog',
            'Psixolog',
            'Fizioterapevt',
            'Radiolog',
            'Infeksionist',
            'Allergolog',
            'Gastroenterolog',
            'Hirurg',
            'Immunolog'
        ]
        
        for spec in specializations:
            Specialization.objects.get_or_create(name=spec)
            self.stdout.write(self.style.SUCCESS(f'Created specialization: {spec}'))

        # Create clinics
        clinics = [
            'Samarqand Davlat Tibbiyot Instituti Klinikasi',
            'Samarqand Shahar Markaziy Shifoxonasi',
            'Samarqand Viloyat Kardiologiya Markazi',
            'Samarqand Pediatriya Markazi',
            'Samarqand Onkologiya Dispanseri',
            'Samarqand Teri Kasalliklari Markazi',
            'Samarqand Endokrinologiya Dispanseri',
            'Samarqand Viloyat Ginekologiya Markazi',
            'Samarqand Urologiya Markazi',
            'Samarqand Travmatologiya Shifoxonasi'
        ]
        
        for clinic in clinics:
            Clinic.objects.get_or_create(name=clinic)
            self.stdout.write(self.style.SUCCESS(f'Created clinic: {clinic}'))

        # Create doctors (50 ta)
        doctors_data = [
            {'name': 'Alisher Aliyev', 'specialization': 'Terapevt'},
            {'name': 'Dilfuza Karimova', 'specialization': 'Kardiolog'},
            {'name': 'Shavkat Rahimov', 'specialization': 'Nevrolog'},
            {'name': 'Zulfiya Yusupova', 'specialization': 'Pediatr'},
            {'name': 'Jamshid Ismoilov', 'specialization': 'Stomatolog'},
            {'name': 'Malika Abdullayeva', 'specialization': 'Oftalmolog'},
            {'name': 'Rustam Tursunov', 'specialization': 'Endokrinolog'},
            {'name': 'Gulnora Mirzayeva', 'specialization': 'Ginekolog'},
            {'name': 'Farhod Usmonov', 'specialization': 'Urolog'},
            {'name': 'Dilbar Rahimova', 'specialization': 'Ortoped'},
            {'name': 'Lola Sobirova', 'specialization': 'Dermatolog'},
            {'name': 'Bekzod Tursunov', 'specialization': 'Onkolog'},
            {'name': 'Amina Rahmatova', 'specialization': 'Reanimatolog'},
            {'name': 'Mirza Aliyev', 'specialization': 'Nefrolog'},
            {'name': 'Zaynab Nurmatova', 'specialization': 'Travmatolog'},
            {'name': 'Kamoliddin Jumaev', 'specialization': 'LOR (Otolarinolog)'},
            {'name': 'Otabek Akhmedov', 'specialization': 'Pulmonolog'},
            {'name': 'Shahnoza Qodirova', 'specialization': 'Psixolog'},
            {'name': 'Javlonbek Akhmedov', 'specialization': 'Fizioterapevt'},
            {'name': 'Turgunbek Sultonov', 'specialization': 'Radiolog'},
            {'name': 'Nasiba Yusupova', 'specialization': 'Infeksionist'},
            {'name': 'Sardorbek Islomov', 'specialization': 'Allergolog'},
            {'name': 'Lola Abdullaeva', 'specialization': 'Gastroenterolog'},
            {'name': 'Maksud Mirzaev', 'specialization': 'Hirurg'},
            {'name': 'Kamola Rahimova', 'specialization': 'Immunolog'}
        ]
        
        # Working hours variants
        working_hours = [
            {'start': '09:00', 'end': '18:00'},  # Standard full day
            {'start': '08:00', 'end': '16:00'},  # Early shift
            {'start': '10:00', 'end': '19:00'},  # Late shift
            {'start': '09:00', 'end': '15:00'},  # Half day
            {'start': '14:00', 'end': '22:00'},  # Evening shift
        ]
        
        for i, doctor_data in enumerate(doctors_data):
            specialization = Specialization.objects.get(name=doctor_data['specialization'])
            clinic = Clinic.objects.order_by('?').first()
            
            # Create user for doctor
            full_name = doctor_data['name']
            username = full_name.lower().replace(' ', '_') + f"_{i}"

            user = get_user_model().objects.create_user(
                username=username,
                password='testpass123',
                first_name=full_name.split()[0],
                last_name=full_name.split()[1]
            )

            doctor = Doctor.objects.create(
                user=user,
                full_name=full_name,
                specialization=specialization,
                clinic=clinic,
                phone=f'+9989{random.randint(10000000, 99999999)}',
                experience_years=random.randint(1, 30),
                bio=f"{full_name} — {specialization.name} mutaxassisi.",
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Doctor created: {full_name}'))

            # Random ish kunlari va vaqtlar
            working_days = random.sample(range(7), random.randint(4, 6))
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
                    f'Schedule for {doctor.full_name} (day {day}) {work_hours["start"]} - {work_hours["end"]}'
                ))

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 
