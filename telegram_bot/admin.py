from django.contrib import admin
from .models import TelegramState

@admin.register(TelegramState)
class TelegramStateAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'state', 'created_at')
    list_filter = ('state',)
    search_fields = ('telegram_id',)
