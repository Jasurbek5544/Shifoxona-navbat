# Shifoxona Navbat Tizimi

Bu loyiha shifoxonalar uchun navbat tizimini boshqarish uchun yaratilgan. Tizim Django framework'ida yozilgan va quyidagi imkoniyatlarni taqdim etadi:

- Bemorlar uchun onlayn navbat olish
- Shifokorlar uchun navbatlarni boshqarish
- Admin panel orqali tizimni boshqarish
- Telegram bot orqali navbat haqida bildirishnomalar

## Texnologiyalar

- Python 3.8+
- Django 5.0
- PostgreSQL
- Telegram Bot API
- Bootstrap 5
- jQuery

## O'rnatish

1. Loyihani klonlang:
```bash
git clone https://github.com/yourusername/shifoxona-navbat.git
cd shifoxona-navbat
```

2. Virtual muhit yarating va faollashtiring:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac uchun
# yoki
venv\Scripts\activate  # Windows uchun
```

3. Kerakli paketlarni o'rnating:
```bash
pip install -r requirements.txt
```

4. `.env` faylini yarating va quyidagi o'zgaruvchilarni to'ldiring:
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=shifoxona
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
TELEGRAM_BOT_TOKEN=your-bot-token
```

5. Ma'lumotlar bazasini yarating va migratsiyalarni o'tkazing:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Superuser yarating:
```bash
python manage.py createsuperuser
```

7. Static fayllarni yig'ing:
```bash
python manage.py collectstatic
```

8. Telegram botni ishga tushiring:
```bash
python manage.py runbot
```

9. Development serverni ishga tushiring:
```bash
python manage.py runserver
```

## Foydalanish

### Bemorlar uchun

1. Bosh sahifaga kiring
2. "Navbat olish" tugmasini bosing
3. Shifokorni tanlang
4. Ma'lumotlaringizni to'ldiring
5. Navbat raqamingizni oling

### Shifokorlar uchun

1. `/accounts/login/` orqali tizimga kiring
2. Dashboard'da navbatlarni ko'ring
3. Navbatlarni boshqaring (boshlash, tugatish, bekor qilish)

### Admin uchun

1. `/admin/` orqali admin panelga kiring
2. Shifokorlar, bemorlar va navbatlarni boshqaring
3. Statistikalarni ko'ring

### Telegram Bot

1. Telegramda botni toping
2. `/start` buyrug'ini yuboring
3. Navbat haqida bildirishnomalar oling

## Fayl tuzilishi

```
shifoxona-navbat/
├── config/             # Asosiy konfiguratsiya
├── core/              # Asosiy funksionallik
├── doctors/           # Shifokorlar uchun funksionallik
├── appointments/      # Navbatlar uchun funksionallik
├── telegram_bot/      # Telegram bot uchun funksionallik
├── static/            # Static fayllar
├── templates/         # HTML shablonlar
├── media/             # Media fayllar
├── requirements.txt   # Kerakli paketlar
└── manage.py          # Django boshqaruv fayli
```

## Xatoliklar

Agar xatolik yuzaga kelsa:

1. 404 xatolik - Sahifa topilmadi
2. 500 xatolik - Server xatoligi
3. Telegram bot ishlamay qolsa - Bot tokenini tekshiring

## Yordam

Agar yordam kerak bo'lsa:
- GitHub Issues orqali xabar bering
- Telegram: @yourusername
- Email: your.email@example.com

## Litsenziya

Bu loyiha MIT litsenziyasi ostida tarqatiladi.

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
