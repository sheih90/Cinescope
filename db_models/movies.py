from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db_models.base import Base  # ← Используем общий Base!
from typing import Dict, Any, Optional
from datetime import datetime


class MovieDBModel(Base):
    """Модель таблицы movies"""
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    price = Column(Integer)
    description = Column(Text)
    image_url = Column(Text)
    location = Column(Text)  # Или используй свой тип Location
    published = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с таблицей genres (опционально)
    genre = relationship("Genre", back_populates="movies")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'location': self.location,
            'published': self.published,
            'rating': self.rating,
            'genre_id': self.genre_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Movie(id={self.id}, name='{self.name}', rating={self.rating})>"