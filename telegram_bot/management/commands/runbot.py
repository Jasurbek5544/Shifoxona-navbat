import logging
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram_bot.handlers import (
    start,
    help_command,
    book_appointment,
    my_appointments,
    cancel_appointment,
    button,
    handle_message,
    handle_contact,
    process_phone_number
)
from telegram import Update

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        """Run the bot."""
        try:
            # Bot tokenini olish
            token = settings.TELEGRAM_BOT_TOKEN

            # Botni yaratish
            application = Application.builder().token(token).build()

            # Command handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("book", book_appointment))
            application.add_handler(CommandHandler("my_appointments", my_appointments))
            application.add_handler(CommandHandler("cancel", cancel_appointment))

            # Callback query handler
            application.add_handler(CallbackQueryHandler(button))

            # Contact handler
            application.add_handler(MessageHandler(filters.CONTACT, process_phone_number))

            # Message handler
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            # Botni ishga tushirish
            self.stdout.write(self.style.SUCCESS('Starting bot...'))
            logger.info('Bot is starting...')
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as error:
            logger.error(f'Error running bot: {str(error)}')
            self.stdout.write(self.style.ERROR(f'Error running bot: {str(error)}')) 