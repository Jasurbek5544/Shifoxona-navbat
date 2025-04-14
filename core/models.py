from django.db import models
from django.utils.translation import gettext_lazy as _

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True

class Clinic(TimeStampedModel):
    """
    Model for storing clinic information
    """
    name = models.CharField(_("Name"), max_length=255)
    address = models.TextField(_("Address"))
    phone = models.CharField(_("Phone"), max_length=20)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        verbose_name = _("Clinic")
        verbose_name_plural = _("Clinics")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ClinicRoom(TimeStampedModel):
    """Model for clinic rooms"""
    name = models.CharField(_("Xona nomi"), max_length=100)
    room_number = models.CharField(_("Xona raqami"), max_length=20)
    description = models.TextField(_("Tavsif"), blank=True)
    is_available = models.BooleanField(_("Mavjud"), default=True)

    class Meta:
        verbose_name = _("Klinika xonasi")
        verbose_name_plural = _("Klinika xonalari")
        ordering = ['room_number']

    def __str__(self):
        return f"{self.name} - {self.room_number}"
