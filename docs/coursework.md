# Курсовий проєкт «Бібліотека» (Варіант 20)

## 1. Мета та обсяг
Мета роботи — розробити тришарову інформаційну систему бібліотеки, що підтримує облік книжкового фонду, читачів, оренди, платежів та сповіщень про прострочення. Додаток надає REST-інтерфейс та веб-інтерфейс на Bootstrap.

## 2. Архітектура
- **Presentation layer** — Flask Blueprints (`controllers/`) з HTML-шаблонами (`templates/`).
- **Service layer** — бізнес-логіка (`services/`) зі Strategy, Observer, Factory Method.
- **Data layer** — SQLAlchemy моделі (`models/`) та Repository-обгортки (`repositories/`).
- **Database** — SQLite (`library.db`) через Singleton `Database`.

### 2.1 Основні компоненти
- `Book`, `Reader`, `Rental`, `Payment`, `Notification` — базові сутності з відношеннями.
- `User` — акаунти з паролями, ролями `admin/user` та прив'язкою до читача.
- `RentalService` — оформлення та повернення прокату, розрахунок знижок і штрафів.
- `ReportService` — звіти за фондом, простроченням, фінансами.
- `NotificationService` — сповіщення про прострочені книги (Observer).
- `AuthService` — реєстрація, аутентифікація, завантаження поточного користувача.
- `StoreController` — клієнтський каталог і оформлення замовлень.

## 3. Використані патерни
| Патерн | Компонент | Призначення |
|--------|-----------|-------------|
| Singleton | `config.Database` | єдиний екземпляр `SQLAlchemy` |
| Factory Method | `services.reader_factory` | створення читачів за категорією |
| Strategy | `services.discount_strategy` | політики знижок |
| Observer | `services.notification_service` | реакція на події прострочення |
| Repository | `repositories.*` | інкапсуляція запитів |

## 4. REST API
| Endpoint | Метод | Опис |
|----------|-------|------|
| `/auth/signup` | GET/POST | самореєстрація користувачів (створює User + Reader) |
| `/auth/login` | GET/POST | вхід у систему, встановлення сесії |
| `/store/` | GET | користувацький каталог з пошуком |
| `/store/rent` | POST | оформлення оренди (форма або JSON) |
| `/store/my-rentals` | GET | історія оренд поточного користувача (HTML/JSON) |
| `/books/` | GET/POST | список, створення книг (admin) |
| `/books/<id>` | GET/PUT/PATCH/DELETE | CRUD для книги (admin) |
| `/readers/` | GET/POST | список, реєстрація читачів (admin) |
| `/rentals/` | GET/POST | перегляд, видача книг (admin) |
| `/rentals/<id>/return` | POST | повернення книги (admin) |
| `/rentals/check-overdue` | POST | запуск перевірки прострочень (admin) |
| `/reports/financial` | GET | фінансовий звіт за період (admin) |
| `/notifications/` | GET | список сповіщень (admin) |

## 5. Бізнес-процеси
1. **Самореєстрація користувача** — форма `/auth/signup`, створення `User` (перший акаунт отримує роль admin) і пов'язаного `Reader`.
2. **Реєстрація читача адміністратором** — форма `readers.html`, Factory Method створює запис відповідної категорії.
3. **Оренда книги** — `RentalService.rent_book`: перевірка наявності, зменшення залишку, створення `Rental`.
4. **Повернення** — `RentalService.return_book`: збільшення залишку, розрахунок знижок і штрафів, створення `Payment`.
5. **Сповіщення** — `RentalService.check_overdue_rentals` → `NotificationService.notify_overdue`, запис у `notifications`.
6. **Звіти** — `ReportService`: агреговані дані для UI та JSON.

## 6. Веб-інтерфейс
Шаблони Jinja2 з Bootstrap:
- `auth/login.html`, `auth/signup.html` — форми входу й реєстрації.
- `store/catalog.html` — користувацький каталог, пошук, оформлення оренд.
- `store/my_rentals.html` — особистий кабінет із переліком оренд.
- `books.html` — таблиця книжок + форма додавання.
- `readers.html` — список читачів, вибір категорій.
- `rentals.html` — активні прокати, повернення, запуск перевірки прострочень.
- `reports.html` — зведення та AJAX-фінансовий звіт.
- `notifications.html` — список сповіщень.

## 7. Тестування
Тести `tests/` покривають:
- реєстрацію та авторизацію користувачів;
- створення читачів через Factory Method;
- розрахунок знижок (Strategy);
- процес повернення книги з нарахуванням штрафу;
- генерацію сповіщень при простроченні.

Запуск: `PYTHONPATH=$PWD pytest`.

## 8. Висновки
Реалізована система відповідає вимогам курсового проєкту, демонструє застосування GoF-патернів і охоплює повний цикл: від самореєстрації користувача та оформлення оренди до фінансових звітів і автоматичних сповіщень. Подальший розвиток може включати email/SMS-сповіщення, інтеграцію з платіжними сервісами, розширені дашборди та аналітику для керування бібліотекою.

