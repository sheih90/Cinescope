from sqlalchemy.orm import Session
from db_models.user import UserDBModel
from db_models.movies import MovieDBModel
from db_models.genre import Genre
from typing import Optional, List
from db_models.account import AccountTransactionTemplate


class DBHelper:
    """Класс с методами для работы с БД в тестах"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    # ========== USERS ==========

    def create_test_user(self, user_dict) -> UserDBModel:
        user = UserDBModel(**user_dict)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def get_user_by_id(self, user_id) -> Optional[UserDBModel]:
        return self.db_session.query(UserDBModel).filter(
            UserDBModel.id == user_id
        ).first()

    def get_user_by_email(self, email: str) -> Optional[UserDBModel]:
        return self.db_session.query(UserDBModel).filter(
            UserDBModel.email == email
        ).first()

    def user_exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        return self.db_session.query(UserDBModel).filter(
            UserDBModel.email == email
        ).count() > 0

    def delete_user(self, user: UserDBModel):
        """Удаляет пользователя"""
        self.db_session.delete(user)
        self.db_session.commit()

    # ========== MOVIES ==========

    def create_test_movie(self, movie_data: dict) -> MovieDBModel:
        """Создает тестовый фильм"""
        movie = MovieDBModel(**movie_data)
        self.db_session.add(movie)
        self.db_session.commit()
        self.db_session.refresh(movie)
        return movie

    def get_movie_by_id(self, movie_id: int) -> Optional[MovieDBModel]:
        """Получает фильм по ID"""
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.id == movie_id
        ).first()

    def get_movie_by_name(self, name: str) -> Optional[MovieDBModel]:
        """Получает фильм по названию"""
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.name == name
        ).first()

    def delete_movie(self, movie: MovieDBModel):
        """Удаляет фильм"""
        self.db_session.delete(movie)
        self.db_session.commit()

    # ========== GENRES ==========

    def get_genre_by_id(self, genre_id: int) -> Optional[Genre]:
        """Получает жанр по ID"""
        return self.db_session.query(Genre).filter(
            Genre.id == genre_id
        ).first()

    def get_genre_by_name(self, name: str) -> Optional[Genre]:
        """Получает жанр по названию"""
        return self.db_session.query(Genre).filter(
            Genre.name == name
        ).first()

    # ========== UTILS ==========

    def cleanup_test_data(self, objects_to_delete: List):
        """Очищает тестовые данные"""
        for obj in objects_to_delete:
            if obj:
                self.db_session.delete(obj)
        self.db_session.commit()

    def rollback(self):
        """Откатывает транзакцию (для тестов)"""
        self.db_session.rollback()

    # ========= MOVIES CHECKS =========

    def movie_exists_by_id(self, movie_id: int) -> bool:
        """Проверяет существование фильма по ID"""
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.id == movie_id
        ).count() > 0

    def movie_exists_by_name(self, name: str) -> bool:
        """Проверяет существование фильма по названию"""
        return self.db_session.query(MovieDBModel).filter(
            MovieDBModel.name == name
        ).count() > 0

    def get_movies_count(self) -> int:
        """Возвращает общее количество фильмов в БД"""
        return self.db_session.query(MovieDBModel).count()

    # ========== ACCOUNTS ==========

    def create_account(self, user: str, balance: int) -> AccountTransactionTemplate:
        """Создаёт новый счёт"""
        account = AccountTransactionTemplate(user=user, balance=balance)
        self.db_session.add(account)
        self.db_session.commit()
        self.db_session.refresh(account)
        return account

    def get_account_by_user(self, user: str) -> AccountTransactionTemplate:
        """Получает счёт по имени пользователя"""
        return self.db_session.query(AccountTransactionTemplate).filter(
            AccountTransactionTemplate.user == user
        ).first()

    def delete_account(self, account: AccountTransactionTemplate):
        """Удаляет счёт"""
        self.db_session.delete(account)
        self.db_session.commit()

    def transfer_money(self, from_user: str, to_user: str, amount: int):
        """
        Переводит деньги между счетами.

        :param from_user: Имя пользователя, с которого списываем
        :param to_user: Имя пользователя, которому зачисляем
        :param amount: Сумма перевода
        :raises ValueError: Если недостаточно средств
        """
        from_account = self.get_account_by_user(from_user)
        to_account = self.get_account_by_user(to_user)

        if not from_account:
            raise ValueError(f"Счёт '{from_user}' не найден")

        if not to_account:
            raise ValueError(f"Счёт '{to_user}' не найден")

        if from_account.balance < amount:
            raise ValueError("Недостаточно средств на счете")

        # Выполняем перевод
        from_account.balance -= amount
        to_account.balance += amount

        self.db_session.commit()

        # Обновляем объекты в сессии
        self.db_session.refresh(from_account)
        self.db_session.refresh(to_account)