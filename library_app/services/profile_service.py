from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from library_app.models.reader import Reader
from library_app.services import rental_repository


@dataclass
class ProfileStats:
    full_name: str
    category: str
    books_read: int
    favorite_genre: str | None


class ProfileService:
    def get_profile_stats(self, reader: Reader) -> ProfileStats:
        """Отримує статистику профілю читача."""
        # Отримуємо всі оренди читача
        rentals = rental_repository.for_reader(reader.id, active_only=False)
        
        # Підраховуємо кількість прочитаних книг (повернених)
        books_read = sum(1 for rental in rentals if rental.is_returned)
        
        # Знаходимо улюблений жанр
        favorite_genre = None
        if rentals:
            genre_counter = Counter()
            for rental in rentals:
                if rental.is_returned:  # Тільки прочитані книги
                    genre_counter[rental.book.genre] += 1
            
            if genre_counter:
                favorite_genre = genre_counter.most_common(1)[0][0]
        
        return ProfileStats(
            full_name=reader.full_name,
            category=reader.category.value,
            books_read=books_read,
            favorite_genre=favorite_genre or "Ще не визначено",
        )


profile_service = ProfileService()

__all__ = ["ProfileService", "ProfileStats", "profile_service"]

