import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.ext import ContextTypes
from django.utils import timezone
from asgiref.sync import sync_to_async
from core.models import Clinic
from doctors.models import Doctor, Specialization
from appointments.models import Patient, Appointment
from .models import TelegramState
import logging

logger = logging.getLogger(__name__)

@sync_to_async
def get_or_create_state(telegram_id):
    return TelegramState.objects.get_or_create(telegram_id=telegram_id)

@sync_to_async
def get_patient(telegram_id):
    try:
        return Patient.objects.get(telegram_id=str(telegram_id))
    except Patient.DoesNotExist:
        return None

@sync_to_async
def create_patient(telegram_id, full_name, phone):
    return Patient.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'full_name': full_name,
            'phone': phone
        }
    )

@sync_to_async
def get_clinics():
    return list(Clinic.objects.all())

@sync_to_async
def get_specializations(clinic_id):
    return list(Specialization.objects.filter(doctors__clinic_id=clinic_id).distinct())

@sync_to_async
def get_doctors(specialization_id):
    return list(Doctor.objects.filter(specialization_id=specialization_id))

@sync_to_async
def get_doctor(doctor_id):
    return Doctor.objects.get(id=doctor_id)

@sync_to_async
def get_schedule(doctor, weekday):
    return doctor.schedules.filter(weekday=weekday, is_working=True).first()

@sync_to_async
def check_appointment_exists(doctor, date, time):
    return Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date,
        appointment_time=time,
        status__in=['pending', 'confirmed']
    ).exists()

@sync_to_async
def get_next_queue_number(doctor, date):
    last_appointment = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date,
        status__in=['pending', 'confirmed']
    ).order_by('-queue_number').first()
    
    if last_appointment:
        return last_appointment.queue_number + 1
    return 1

@sync_to_async
def create_appointment(patient, doctor, date):
    last_appointment = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date
    ).order_by('-queue_number').first()
    
    queue_number = 1 if not last_appointment else last_appointment.queue_number + 1

    return Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        appointment_date=date,
        queue_number=queue_number,
        status='pending'
    )

@sync_to_async
def get_appointments(patient):
    return list(Appointment.objects.filter(
        patient=patient,
        status__in=['pending', 'confirmed']
    ).order_by('-appointment_date'))

@sync_to_async
def cancel_appointment_by_id(appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if appointment.status in ['pending', 'confirmed']:
        appointment.cancel(reason='Bemor tomonidan bekor qilindi', cancelled_by_patient=True)
        return appointment
    return None

@sync_to_async
def get_doctor_with_specialization_and_clinic(doctor_id):
    return Doctor.objects.select_related('specialization', 'clinic').get(id=doctor_id)

@sync_to_async
def get_doctors_with_specialization_and_clinic(clinic_id):
    return list(Doctor.objects.filter(clinic_id=clinic_id, is_active=True).select_related('specialization', 'clinic'))

@sync_to_async
def check_schedule_exists(doctor, weekday):
    return doctor.schedules.filter(weekday=weekday, is_working=True).exists()

@sync_to_async
def get_doctor_with_clinic(doctor_id):
    return Doctor.objects.select_related('clinic').get(id=doctor_id)

@sync_to_async
def get_appointment_with_doctor(appointment_id):
    return Appointment.objects.select_related(
        'doctor',
        'doctor__clinic',
        'doctor__specialization'
    ).get(id=appointment_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botni ishga tushirish"""
    user = update.effective_user
    patient = await get_patient(user.id)
    
    if not patient:
        # Ask for phone number if user is not registered
        keyboard = [[
            InlineKeyboardButton("📱 Telefon raqamni yuborish", callback_data="send_phone")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Assalomu alaykum {user.first_name}!\n\n"
            "Men Shifokor Navbat botiman. Men sizga shifokorlarga navbat olishda yordam beraman.\n\n"
            "Botdan foydalanish uchun avval telefon raqamingizni yuboring:",
            reply_markup=reply_markup
        )
        return
    
    # If user is already registered, show main menu with permanent buttons
    reply_markup = ReplyKeyboardMarkup(
        [
            ["📝 Navbatga yozilish"],
            ["📋 Mening navbatlarim"]
        ],
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        f"Assalomu alaykum {user.first_name}!\n\n"
        "Men Shifokor Navbat botiman. Men sizga shifokorlarga navbat olishda yordam beraman.\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyrug'i"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Navbatga yozilish", callback_data="book"),
            InlineKeyboardButton("📋 Mening navbatim", callback_data="my_appointments")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Bot buyruqlari:\n\n"
        "/start - Botni ishga tushirish\n"
        "/book - Navbat olish\n"
        "/my_appointments - Mening navbatlarim\n"
        "/cancel - Navbatni bekor qilish\n"
        "/help - Yordam\n\n"
        "Yoki quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup
    )

async def book_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Navbat olish jarayoni"""
    clinics = await get_clinics()
    keyboard = []
    for clinic in clinics:
        keyboard.append([
            InlineKeyboardButton(clinic.name, callback_data=f"clinic_{clinic.id}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "Klinikani tanlang:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Klinikani tanlang:",
            reply_markup=reply_markup
        )

async def my_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchining navbatlarini ko'rsatish"""
    user = update.effective_user
    patient = await get_patient(user.id)
    
    if not patient:
        message = "Siz hali navbat olmagan ekansiz."
        if update.callback_query:
            await update.callback_query.message.edit_text(message)
        else:
            await update.message.reply_text(message)
        return

    appointments = await get_appointments(patient)
    
    if not appointments:
        message = "Sizda hozircha navbatlar mavjud emas."
        if update.callback_query:
            await update.callback_query.message.edit_text(message)
        else:
            await update.message.reply_text(message)
        return

    message = "Sizning navbatlaringiz:\n\n"
    for appointment in appointments:
        appointment = await get_appointment_with_doctor(appointment.id)
        status = {
            'pending': '⏳ Kutilmoqda',
            'confirmed': '✅ Tasdiqlangan'
        }.get(appointment.status, appointment.status)
        
        message += (
            f"👨‍⚕️ Shifokor: {appointment.doctor.full_name}\n"
            f"""📚 Mutaxassislik: {appointment.doctor.specialization.name if appointment.doctor.specialization else "Mutaxassislik ko'rsatilmagan"}
"""
            f"🏥 Klinika: {appointment.doctor.clinic.name}\n"
            f"📅 Sana: {appointment.appointment_date.strftime('%Y-%m-%d')}\n"
            f"🔄 Navbat raqami: {appointment.queue_number}\n"
            f"📝 Holat: {status}\n"
        )
        if appointment.notes:
            message += f"💬 Izoh: {appointment.notes}\n"
        
        # Add cancel button for active appointments
        keyboard = []
        if appointment.status in ['pending', 'confirmed']:
            keyboard.append([
                InlineKeyboardButton("❌ Navbatni bekor qilish", callback_data=f"cancel_{appointment.id}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.message.edit_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        message = ""  # Reset message for next appointment

async def cancel_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Navbatni bekor qilish"""
    user = update.effective_user
    try:
        patient = Patient.objects.get(telegram_id=str(user.id))
        appointments = Appointment.objects.filter(
            patient=patient,
            status__in=['pending', 'confirmed']
        )
        
        if not appointments.exists():
            await update.message.reply_text("Sizda bekor qilinadigan navbatlar mavjud emas.")
            return

        keyboard = []
        for appointment in appointments:
            doctor = appointment.doctor
            keyboard.append([
                InlineKeyboardButton(
                    f"{doctor.full_name} - {appointment.appointment_date.strftime('%Y-%m-%d')}",
                    callback_data=f"cancel_{appointment.id}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Qaysi navbatni bekor qilmoqchisiz?",
            reply_markup=reply_markup
        )
    except Patient.DoesNotExist:
        await update.message.reply_text("Siz hali navbat olmagan ekansiz.")

async def select_specialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mutaxassislikni tanlash"""
    query = update.callback_query
    clinic_id = int(query.data.split('_')[1])
    
    # Get specializations for the selected clinic
    specializations = await get_specializations(clinic_id)
    
    if not specializations:
        await query.message.edit_text(
            "Kechirasiz, bu klinikada hozircha mutaxassisliklar mavjud emas.\n"
            "Iltimos, boshqa klinikani tanlang.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Orqaga", callback_data="book")
            ]])
        )
        return
    
    keyboard = []
    for spec in specializations:
        keyboard.append([
            InlineKeyboardButton(spec.name, callback_data=f"specialization_{spec.id}")
        ])
    
    # Add back button
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="book")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "Mutaxassislikni tanlang:",
        reply_markup=reply_markup
    )

async def select_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE, specialization_id):
    """Shifokorni tanlash"""
    doctors = await get_doctors(specialization_id)
    keyboard = []
    for doctor in doctors:
        keyboard.append([
            InlineKeyboardButton(doctor.full_name, callback_data=f"doctor_{doctor.id}")
        ])
    
    # Add back button to specializations list
    if doctors:
        # Get the first doctor's clinic ID using sync_to_async
        first_doctor = await sync_to_async(lambda: doctors[0].clinic.id)()
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"clinic_{first_doctor}")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="book")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        "Shifokorni tanlang:",
        reply_markup=reply_markup
    )

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE, doctor_id):
    """Sana tanlash"""
    doctor = await get_doctor(doctor_id)
    today = timezone.now().date()
    dates = []
    
    for i in range(7):  # Keyingi 7 kun
        date = today + timedelta(days=i)
        exists = await check_schedule_exists(doctor, date.weekday())
        if exists:
            dates.append(date)
    
    if not dates:
        await update.callback_query.message.edit_text(
            "Kechirasiz, shifokor uchun mavjud kunlar topilmadi.\n"
            "Boshqa shifokorni tanlang yoki keyinroq qayta urinib ko'ring."
        )
        return

    keyboard = []
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        formatted_date = date.strftime('%d.%m.%Y')
        keyboard.append([
            InlineKeyboardButton(
                formatted_date,
                callback_data=f"date_{doctor_id}_{date_str}"
            )
        ])
    
    # Add back button to doctors list
    # Get specialization ID using sync_to_async
    specialization_id = await sync_to_async(lambda: doctor.specialization.id if doctor.specialization else None)()
    if specialization_id:
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"specialization_{specialization_id}")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="book")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text(
        "Navbat olish uchun sanani tanlang:",
        reply_markup=reply_markup
    )

async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE, doctor_id, date_str):
    """Navbatni tasdiqlash"""
    doctor = await get_doctor_with_clinic(doctor_id)
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{doctor_id}_{date_str}"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"date_{doctor_id}_{date_str}")
        ]
    ]
    
    # Add back button to date selection
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data=f"doctor_{doctor_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get next queue number
    queue_number = await get_next_queue_number(doctor, date)
    
    # Get specialization name using sync_to_async
    specialization_name = await sync_to_async(lambda: doctor.specialization.name if doctor.specialization else "Mutaxassislik ko'rsatilmagan")()
    
    message = (
        f"Shifokor: {doctor.full_name}\n"
        f"Mutaxassislik: {specialization_name}\n"
        f"Klinika: {doctor.clinic.name}\n"
        f"Sana: {date.strftime('%d.%m.%Y')}\n"
        f"Navbat raqami: {queue_number}\n\n"
        "Navbatni tasdiqlaysizmi?"
    )
    
    await update.callback_query.message.edit_text(message, reply_markup=reply_markup)

async def save_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE, doctor_id, date_str):
    """Navbatni saqlash"""
    user = update.effective_user
    doctor = await get_doctor_with_clinic(doctor_id)
    date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Bemor ma'lumotlarini saqlash yoki yangilash
    patient, created = await sync_to_async(Patient.objects.get_or_create)(
        telegram_id=str(user.id),
        defaults={
            'full_name': f"{user.first_name} {user.last_name or ''}".strip(),
            'phone': None  # Telefon raqamini keyinroq so'raladi
        }
    )

    # Navbatni yaratish
    appointment = await create_appointment(patient, doctor, date)

    keyboard = [
        [
            InlineKeyboardButton("📋 Mening navbatim", callback_data="my_appointments")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        f"Navbat muvaffaqiyatli yaratildi!\n\n"
        f"👨‍⚕️ Shifokor: {doctor.full_name}\n"
        f"🏥 Klinika: {doctor.clinic.name}\n"
        f"📅 Sana: {date_str}\n"
        f"🔄 Navbat raqami: {appointment.queue_number}\n\n"
        "Navbatlaringizni ko'rish uchun 'Mening navbatim' tugmasini bosing.",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Contact message handler"""
    user = update.effective_user
    contact = update.message.contact
    
    # Get phone number
    phone = contact.phone_number
    if not phone.startswith('+'):
        phone = '+' + phone
    
    # Create or update patient
    patient, created = await create_patient(
        telegram_id=str(user.id),
        full_name=user.full_name,
        phone=phone
    )
    
    # Remove the keyboard
    await update.message.reply_text(
        "Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
        "Endi navbat olish uchun quyidagi tugmalardan birini tanlang:",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Show main menu with permanent buttons
    reply_markup = ReplyKeyboardMarkup(
        [
            ["📝 Navbatga yozilish"],
            ["📋 Mening navbatlarim"]
        ],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xabar qabul qilganda"""
    user = update.effective_user
    text = update.message.text
    
    if text == "📝 Navbatga yozilish":
        await book_appointment(update, context)
    elif text == "📋 Mening navbatlarim":
        await my_appointments(update, context)
    elif text == "/my_appointments":
        await my_appointments(update, context)
    else:
        # Create keyboard with permanent buttons
        reply_markup = ReplyKeyboardMarkup(
            [
                ["📝 Navbatga yozilish"],
                ["📋 Mening navbatlarim"]
            ],
            resize_keyboard=True
        )
        await update.message.reply_text(
            "Iltimos, quyidagi tugmalardan birini tanlang:",
            reply_markup=reply_markup
        )

async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamni qayta ishlash"""
    query = update.callback_query
    user = update.effective_user
    
    keyboard = [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await query.message.reply_text(
        "Iltimos, telefon raqamingizni yuboring.\n"
        "Buning uchun quyidagi '📱 Telefon raqamni yuborish' tugmasini bosing:",
        reply_markup=reply_markup
    )

async def process_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yuborilgan telefon raqamni qayta ishlash"""
    user = update.effective_user
    contact = update.message.contact
    
    if not contact or str(contact.user_id) != str(user.id):
        await update.message.reply_text(
            "Iltimos, '📱 Telefon raqamni yuborish' tugmasini bosing."
        )
        return
    
    # Create patient
    patient, created = await create_patient(
        telegram_id=str(user.id),
        full_name=user.full_name or f"User {user.id}",
        phone=contact.phone_number
    )
    
    # Show main menu
    keyboard = [
        [
            InlineKeyboardButton("📝 Navbatga yozilish", callback_data="book"),
            InlineKeyboardButton("📋 Mening navbatim", callback_data="my_appointments")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
        f"Endi siz navbat olishingiz mumkin.\n"
        f"Buning uchun quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalarni qayta ishlash"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start":
        await start(update, context)
    elif query.data == "book":
        await book_appointment(update, context)
    elif query.data == "my_appointments":
        await my_appointments(update, context)
    elif query.data.startswith("clinic_"):
        await select_specialization(update, context)
    elif query.data.startswith("specialization_"):
        specialization_id = int(query.data.split('_')[1])
        await select_doctor(update, context, specialization_id)
    elif query.data.startswith("doctor_"):
        doctor_id = int(query.data.split('_')[1])
        await select_date(update, context, doctor_id)
    elif query.data.startswith("date_"):
        _, doctor_id, date_str = query.data.split('_')
        await confirm_appointment(update, context, int(doctor_id), date_str)
    elif query.data.startswith("confirm_"):
        _, doctor_id, date_str = query.data.split('_')
        await save_appointment(update, context, int(doctor_id), date_str)
    elif query.data.startswith("cancel_"):
        await cancel_appointment(update, context) 