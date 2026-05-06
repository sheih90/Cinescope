from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_models.base import Base


class Genre(Base):
    """Модель таблицы genres"""
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    movies = relationship("MovieDBModel", back_populates="genre")

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """Конвертирует объект в словарь"""
        return {
            "id": self.id,
            "name": self.name
        }