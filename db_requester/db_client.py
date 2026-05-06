from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from resources.db_creds import movies_db_creds

# Создаём движок (engine) для подключения к БД
engine = create_engine(
    movies_db_creds.get_connection_string(),
    echo=False  # True = логировать все SQL-запросы (для отладки)
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()


def execute_raw_query(query: str, params: dict = None):
    """
    Выполняет сырой SQL-запрос и возвращает результаты.

    :param  SQL-запрос с параметрами (:param_name)
    :param params: Словарь параметров для подстановки
    :return: Список кортежей с результатами
    """
    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        return result.fetchall()


# Контекстный менеджер для сессии (опционально, но удобно)
from contextlib import contextmanager


@contextmanager
def get_db_session_context():
    """Контекстный менеджер для автоматического закрытия сессии"""
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()