from django import forms
from .models import Appointment
from datetime import date, timedelta

class AppointmentForm(forms.Form):
    full_name = forms.CharField(
        label='Ism va Familiya',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label='Telefon raqam',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    appointment_date = forms.ChoiceField(
        label='Navbat kuni',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        label='Tashrif sababi',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        
        if doctor:
            # Generate next 7 days
            today = date.today()
            days = []
            for i in range(7):
                current_date = today + timedelta(days=i)
                # Check if it's a working day
                weekday = current_date.weekday()
                if weekday < 5:  # Monday to Friday
                    days.append((current_date.strftime('%Y-%m-%d'), 
                               current_date.strftime('%d.%m.%Y')))
            
            self.fields['appointment_date'].choices = days 