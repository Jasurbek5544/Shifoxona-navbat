from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from doctors.models import Doctor
from django.utils import timezone

class Patient(TimeStampedModel):
    """
    Model for storing patient information
    """
    full_name = models.CharField(_("Full name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=20)
    telegram_id = models.CharField(_("Telegram ID"), max_length=255, unique=True)
    is_blocked = models.BooleanField(_("Is blocked"), default=False)

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

class Appointment(TimeStampedModel):
    """
    Model for storing appointment information
    """
    STATUS_CHOICES = [
        ('pending', _("Kutilayotgan")),
        ('confirmed', _("Tasdiqlangan")),
        ('cancelled', _("Bekor qilingan")),
        ('completed', _("Bajarilgan")),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField(_("Navbat sanasi"))
    queue_number = models.PositiveIntegerField(_("Navbat raqami"))
    status = models.CharField(_("Holat"), max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_("Eslatmalar"), blank=True)
    cancellation_reason = models.TextField(_("Bekor qilish sababi"), blank=True)
    cancelled_by_patient = models.BooleanField(_("Bemor tomonidan bekor qilingan"), default=False)
    confirmed_at = models.DateTimeField(_("Tasdiqlangan vaqti"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Bajarilgan vaqti"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("Bekor qilingan vaqti"), null=True, blank=True)

    class Meta:
        verbose_name = _("Navbat")
        verbose_name_plural = _("Navbatlar")
        ordering = ['-appointment_date', 'queue_number']
        unique_together = ['doctor', 'appointment_date', 'queue_number']

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.appointment_date}"

    def confirm(self):
        """Navbatni tasdiqlash"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
            self.save()
            return True
        return False

    def complete(self):
        """Navbatni bajarilgan deb belgilash"""
        if self.status == 'confirmed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False

    def cancel(self, reason='', cancelled_by_patient=False):
        """Navbatni bekor qilish"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            self.cancellation_reason = reason
            self.cancelled_at = timezone.now()
            self.cancelled_by_patient = cancelled_by_patient
            self.save()

            # Agar bemor bekor qilsa, navbat ketma-ketligini yangilash
            if cancelled_by_patient:
                # Keyingi navbatlarni bir orqaga surish
                next_appointments = Appointment.objects.filter(
                    doctor=self.doctor,
                    appointment_date=self.appointment_date,
                    queue_number__gt=self.queue_number,
                    status__in=['pending', 'confirmed']
                ).order_by('queue_number')

                for appointment in next_appointments:
                    appointment.queue_number -= 1
                    appointment.save()

            return True
        return False

class Queue(TimeStampedModel):
    """
    Model for managing doctor's daily queue
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='queues')
    date = models.DateField(_("Date"))
    current_number = models.PositiveIntegerField(_("Current number"), default=0)
    last_number = models.PositiveIntegerField(_("Last number"), default=0)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Queue")
        verbose_name_plural = _("Queues")
        ordering = ['-date', 'doctor']
        unique_together = ['doctor', 'date']

    def __str__(self):
        return f"{self.doctor} - {self.date}"

    def get_next_number(self):
        """
        Returns the next available queue number
        """
        if not self.is_active:
            return None
        self.last_number += 1
        self.save()
        return self.last_number
