# Shifoxona Navbat - Doctor Appointment System

A comprehensive doctor appointment management system with a Telegram bot interface, built with Django.

## Features

- 🏥 Clinic and doctor management
- 📅 Online appointment scheduling
- 🤖 Telegram bot for easy access
- 👨‍⚕️ Doctor specialization management
- 📱 Patient registration and management
- 🔄 Queue number management
- 📊 Admin dashboard
- 🔔 Appointment notifications

## Tech Stack

- Python 3.8+
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Telegram Bot API
- Bootstrap 5
- jQuery

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Telegram Bot Token
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/shifokor_navbat.git
cd shifokor_navbat
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Start the Telegram bot in a separate terminal:
```bash
python manage.py runbot
```

## Project Structure

```
shifokor_navbat/
├── core/                 # Core app with shared functionality
├── doctors/             # Doctor and clinic management
├── appointments/        # Appointment management
├── telegram_bot/        # Telegram bot implementation
├── templates/           # HTML templates
├── static/             # Static files
└── manage.py           # Django management script
```

## Telegram Bot Commands

- `/start` - Start the bot
- `/help` - Show help information
- `/book` - Book a new appointment
- `/my_appointments` - View your appointments
- `/cancel` - Cancel an appointment

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django team for the amazing framework
- Telegram team for the Bot API
- All contributors and users of the system

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Roadmap

- [ ] Add payment integration
- [ ] Implement SMS notifications
- [ ] Add multi-language support
- [ ] Create mobile app
- [ ] Add analytics dashboard

---

# Shifoxona Navbat - Shifokorlarga Navbat Olish Tizimi

Django asosida qurilgan, Telegram bot interfeysiga ega keng qamrovli shifokorlarga navbat olish tizimi.

## Imkoniyatlar

- 🏥 Klinika va shifokorlarni boshqarish
- 📅 Onlayn navbat olish
- 🤖 Telegram bot orqali oson foydalanish
- 👨‍⚕️ Shifokor mutaxassisliklarini boshqarish
- 📱 Bemorlarni ro'yxatga olish va boshqarish
- 🔄 Navbat raqamlarini boshqarish
- 📊 Admin panel
- 🔔 Navbat haqida bildirishnomalar

## Texnologiyalar

- Python 3.8+
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Telegram Bot API
- Bootstrap 5
- jQuery

## Talablar

- Python 3.8 yoki undan yuqori versiya
- PostgreSQL
- Telegram Bot Token
- Virtual muhit (tavsiya etiladi)

## O'rnatish

1. Repozitoriyani klonlash:
```bash
git clone git@github.com:Jasurbek5544/Shifoxona-navbat.git
cd Shifoxona-navbat
```

2. Virtual muhit yaratish va faollashtirish:
```bash
python -m venv venv
source venv/bin/activate  # Windows uchun: venv\Scripts\activate
```

3. Kerakli paketlarni o'rnatish:
```bash
pip install -r requirements.txt
```

4. `.env` faylini yaratish va quyidagi o'zgaruvchilarni qo'shish:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

5. Migratsiyalarni ishga tushirish:
```bash
python manage.py migrate
```

6. Superuser yaratish:
```bash
python manage.py createsuperuser
```

7. Rivojlanish serverini ishga tushirish:
```bash
python manage.py runserver
```

8. Telegram botni alohida terminalda ishga tushirish:
```bash
python manage.py runbot
```

## Loyiha Tuzilishi

```
Shifoxona-navbat/
├── core/                 # Asosiy funksionallik
├── doctors/             # Shifokor va klinika boshqaruvi
├── appointments/        # Navbat boshqaruvi
├── telegram_bot/        # Telegram bot
├── templates/           # HTML shablonlar
├── static/             # Statik fayllar
└── manage.py           # Django boshqaruv skripti
```

## Telegram Bot Buyruqlari

- `/start` - Botni ishga tushirish
- `/help` - Yordam ma'lumotlari
- `/book` - Yangi navbat olish
- `/my_appointments` - Navbatlaringizni ko'rish
- `/cancel` - Navbatni bekor qilish

## Ishtirok Etish

1. Repozitoriyani fork qiling
2. Yangi branch yarating (`git checkout -b feature/yangi-imkoniyat`)
3. O'zgarishlarni commit qiling (`git commit -m 'Yangi imkoniyat qo'shildi'`)
4. Branchga push qiling (`git push origin feature/yangi-imkoniyat`)
5. Pull Request oching

## Litsenziya

Bu loyiha MIT litsenziyasi ostida litsenziyalangan - batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## Minnatdorchilik

- Django jamoasi ajoyib framework uchun
- Telegram jamoasi Bot API uchun
- Loyihada ishtirok etgan barcha ishtirokchilar va foydalanuvchilar

## Yordam

Yordam uchun GitHub repozitoriyasida issue oching yoki loyiha egasiga murojaat qiling.

## Reja

- [ ] To'lov integratsiyasi
- [ ] SMS bildirishnomalar
- [ ] Ko'p tilli qo'llab-quvvatlash
- [ ] Mobil ilova
- [ ] Analitika paneli 
