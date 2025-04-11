from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class TelegramState(TimeStampedModel):
    """
    Model for storing telegram bot states for users
    """
    telegram_id = models.CharField(_("Telegram ID"), max_length=50, unique=True)
    state = models.CharField(_("State"), max_length=50)
    data = models.JSONField(_("Data"), default=dict)

    class Meta:
        verbose_name = _("Telegram State")
        verbose_name_plural = _("Telegram States")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.telegram_id} - {self.state}"
