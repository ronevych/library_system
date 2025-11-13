# Library Information System (Variant 20)

Курсовий проєкт із дисципліни «Документування програмного забезпечення та шаблони проектування». Система реалізує веб-додаток бібліотеки з керуванням книжковим фондом, читачами та процесом прокату.

## Технології
- Python 3.12
- Flask 3
- Flask-SQLAlchemy / SQLite 3
- Jinja2 + Bootstrap 5
- Pytest

## Структура
```
library_app/
├── app.py                  # Flask application factory
├── config.py               # Конфігурація та Singleton для SQLAlchemy
├── models/                 # SQLAlchemy моделі
├── repositories/           # Repository layer
├── services/               # Бізнес-логіка та патерни
├── controllers/            # REST-контролери (Blueprints)
├── templates/              # HTML шаблони (Bootstrap)
├── static/                 # Статичні файли
├── report/                 # Діаграми (.png)
└── docs/                   # Документація курсового проєкту
```

## Патерни проєктування
- **Singleton** `config.Database` — єдиний екземпляр `SQLAlchemy`.
- **Factory Method** `services.reader_factory` — створення читачів різних категорій.
- **Strategy** `services.discount_strategy` — різні політики знижок.
- **Observer** `services.notification_service` — сповіщення про прострочення.
- **Repository** `repositories.*` — шар доступу до даних.

## Аутентифікація та ролі
- Самореєстрація і вхід доступні на `/auth/signup` та `/auth/login`.
- Перший зареєстрований користувач автоматично отримує роль **admin**, наступні — **user**.
- Адмін-розділи (книги, читачі, прокат, звіти, сповіщення) захищені декоратором `admin_required`.
- Користувачі з роллю `user` можуть оформлювати оренду лише від власного профілю читача.

## Клієнтський інтерфейс
- `/store/` — каталог книг у форматі e-commerce з пошуком за назвою, автором чи жанром.
- `/store/rent` — оформлення оренди (HTML-форма або JSON POST).
- `/store/my-rentals` — особистий кабінет із переліком активних та завершених оренд.

## Адмін-можливості
- `/books`, `/readers`, `/rentals`, `/reports`, `/notifications` — повний набір CRUD і звітів з Bootstrap UI.
- Адмінські API повертають коди 401/403 для неавторизованих запитів (JSON-відповідь із деталями).

## Налаштування середовища
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ініціалізація бази даних
```bash
python - <<'PY'
from library_app import create_app
from library_app.models import db

app = create_app()
with app.app_context():
    db.create_all()
PY
```

## Запуск
```bash
export FLASK_APP=library_app.app:create_app
flask run
```
або
```bash
python library_app/app.py
```

Після запуску перейдіть на `http://127.0.0.1:5000/` (перенаправлення у каталог `/store/`).

> Рекомендовано встановити `export FLASK_SECRET_KEY="..."`
> для безпечних сесій у production режимі.

## Тестування
```bash
PYTHONPATH=$PWD pytest
```

## Документація
- `docs/coursework.md` — опис архітектури, тестів, висновків.
- `report/use_case_diagram.png` — діаграма варіантів використання.
- `report/class_diagram.png` — діаграма класів.
- `theory.txt` — тези та план захисту.

