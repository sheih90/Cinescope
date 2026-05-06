from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from db_models.base import Base  # ← Используем общий Base
from typing import Dict, Any


class UserDBModel(Base):
    """Модель таблицы users"""
    __tablename__ = 'users'

    id = Column(String, primary_key=True)  # UUID в БД
    email = Column(String, nullable=False)
    full_name = Column(String)
    password = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    roles = Column(String)  # Хранится как текст '{USER,ADMIN}'

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'password': self.password,  # ⚠️ В реальных тестах не возвращай пароль!
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'verified': self.verified,
            'banned': self.banned,
            'roles': self.roles
        }

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"