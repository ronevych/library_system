from datetime import date, timedelta

from library_app.models import db
from library_app.models.book import Book
from library_app.models.reader import ReaderCategory
from library_app.services.discount_strategy import DiscountContext, strategy_for_category
from library_app.services.notification_service import NotificationService
from library_app.services.reader_factory import get_reader_creator
from library_app.services.rental_service import rental_service
from library_app.services import (
    book_repository,
    notification_repository,
    reader_repository,
    rental_repository,
    payment_repository,
)


def create_sample_data():
    book = Book(
        title="Володар Перснів",
        author="Дж.Р.Р. Толкін",
        genre="Фентезі",
        collateral_value=100.0,
        daily_rent_price=10.0,
        available_copies=3,
    )
    book_repository.add(book)

    reader = get_reader_creator(ReaderCategory.REGULAR).create_reader(
        full_name="Іван Петренко",
        address="вул. Центральна, 1",
        phone="+380000000000",
    )
    reader_repository.add(reader)
    return book, reader


def test_reader_factory_creates_expected_category(app):
    _, reader = create_sample_data()
    assert reader.category == ReaderCategory.REGULAR

    vip_reader = get_reader_creator(ReaderCategory.VIP).create_reader(
        full_name="VIP Гість",
        address="пр. Свободи, 10",
        phone="+380111111111",
    )
    reader_repository.add(vip_reader)
    assert vip_reader.category == ReaderCategory.VIP


def test_strategy_discount_values():
    vip_strategy = strategy_for_category(ReaderCategory.VIP)
    context = DiscountContext(vip_strategy)
    assert context.calculate(100.0) == 80.0

    regular = strategy_for_category(ReaderCategory.REGULAR)
    assert DiscountContext(regular).calculate(100.0) == 100.0


def test_rental_return_creates_payment_and_fine(app):
    book, reader = create_sample_data()

    rental = rental_service.rent_book(book.id, reader.id, days=2)

    rental.rent_date = date.today() - timedelta(days=5)
    rental.due_date = rental.rent_date + timedelta(days=2)
    db.session.commit()

    summary = rental_service.return_book(
        rental.id, return_date=rental.rent_date + timedelta(days=5)
    )

    assert summary.amount_due > 0
    assert summary.fine_amount > 0
    assert summary.days_rented == 5
    payments = payment_repository.all()
    assert len(list(payments)) == 1
    db.session.refresh(book)
    assert book.available_copies == 3


def test_overdue_notification_generated(app):
    NotificationService.bootstrap()
    book, reader = create_sample_data()
    rental = rental_service.rent_book(book.id, reader.id, days=1)
    rental.due_date = date.today() - timedelta(days=3)
    rental.rent_date = rental.due_date - timedelta(days=2)
    db.session.commit()

    notification_repository.all()  # ensure lazy init
    NotificationService.notify_overdue(rental)

    notifications = list(notification_repository.all())
    assert len(notifications) == 1
    assert reader.full_name in notifications[0].message

