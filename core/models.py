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
