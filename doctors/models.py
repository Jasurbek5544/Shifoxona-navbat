from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, Clinic

class Specialization(TimeStampedModel):
    """
    Model for storing doctor specializations
    """
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Specialization")
        verbose_name_plural = _("Specializations")
        ordering = ['name']

    def __str__(self):
        return self.name

class Doctor(TimeStampedModel):
    """
    Model for storing doctor information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors')
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name='doctors')
    full_name = models.CharField(_("Full name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=20)
    experience_years = models.PositiveIntegerField(_("Years of experience"), default=0)
    bio = models.TextField(_("Biography"), blank=True)
    photo = models.ImageField(_("Photo"), upload_to='doctors/', blank=True, null=True)
    is_active = models.BooleanField(_("Is active"), default=True)
    years_of_experience = models.IntegerField(_("Tajriba yili"), default=0)

    class Meta:
        verbose_name = _("Doctor")
        verbose_name_plural = _("Doctors")
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

class Schedule(TimeStampedModel):
    """
    Model for storing doctor's work schedule
    """
    WEEKDAYS = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(_("Weekday"), choices=WEEKDAYS)
    start_time = models.TimeField(_("Start time"))
    end_time = models.TimeField(_("End time"))
    is_working = models.BooleanField(_("Is working"), default=True)

    class Meta:
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ['weekday', 'start_time']
        unique_together = ['doctor', 'weekday']

    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()}"
