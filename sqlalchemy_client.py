from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Text, ForeignKey, text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from resources.db_creds import db_creds

# Формируем URL для подключения к базе
creds = db_creds.get_connection_params()
connection_string = f"postgresql+psycopg2://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['dbname']}"

# Создаём движок (engine)
engine = create_engine(connection_string)

# Базовый класс для моделей
Base = declarative_base()


# ============================================
# МОДЕЛИ ТАБЛИЦ
# ============================================

class Genre(Base):
    """Модель таблицы genres"""
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class Movie(Base):
    """Модель таблицы movies"""
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    name = Column(Text)  # ← Было title, стало name
    price = Column(Integer)
    description = Column(Text)
    image_url = Column(Text)
    location = Column(Text)  # Или используй свой тип Location
    published = Column(Boolean)
    rating = Column(Float)  # ← float8 в Python это float
    genre_id = Column(Integer, ForeignKey('genres.id'))
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<Movie(id={self.id}, name='{self.name}', rating={self.rating})>"


# ============================================
# ПРИМЕР 1: RAW SQL (прямые SQL-запросы)
# ============================================

def raw_sql_example():
    """Пример выполнения SQL-запроса через SQLAlchemy Core"""
    print("\n" + "=" * 80)
    print("📊 ПРИМЕР 1: RAW SQL запрос")
    print("=" * 80)

    query = """
    SELECT id, name 
    FROM genres 
    ORDER BY id DESC 
    LIMIT 10;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        print("\n📁 Последние 10 жанров:")
        for row in result:
            print(f"  ID: {row[0]}, Название: {row[1]}")


# ============================================
# ПРИМЕР 2: ORM (работа с объектами)
# ============================================

def orm_example():
    """Пример работы с ORM SQLAlchemy"""
    print("\n" + "=" * 80)
    print("️ ПРИМЕР 2: ORM запрос")
    print("=" * 80)

    # Создаём сессию
    Session = sessionmaker(bind=engine)
    session = Session()

    # === SELECT ===
    print("\n📋 Получаем все жанры:")
    genres = session.query(Genre).all()
    for genre in genres:
        print(f"  {genre}")

    # === SELECT с фильтром ===
    print("\n🔍 Ищем жанр по ID:")
    genre_id = 1
    genre = session.query(Genre).filter(Genre.id == genre_id).first()
    if genre:
        print(f"  Найден: {genre}")
    else:
        print(f"  Жанр с ID {genre_id} не найден")

    # === INSERT ===
    print("\n➕ Добавляем новый жанр:")
    new_genre = Genre(name="Фантастический боевик")
    session.add(new_genre)
    session.commit()
    print(f"  ✅ Добавлен жанр с ID: {new_genre.id}")

    # === UPDATE ===
    print("\n✏️ Обновляем жанр:")
    genre_to_update = session.query(Genre).filter(Genre.id == new_genre.id).first()
    if genre_to_update:
        genre_to_update.name = "Научная фантастика"
        session.commit()
        print(f"  ✅ Обновлён: {genre_to_update}")

    # === DELETE ===
    print("\n🗑️ Удаляем жанр:")
    genre_to_delete = session.query(Genre).filter(Genre.id == new_genre.id).first()
    if genre_to_delete:
        session.delete(genre_to_delete)
        session.commit()
        print(f"  ✅ Удалён жанр ID: {new_genre.id}")

    # Закрываем сессию
    session.close()


# ============================================
# ПРИМЕР 3: Сложный запрос с JOIN
# ============================================

def join_example():
    """Пример запроса с JOIN"""
    print("\n" + "=" * 80)
    print("🔗 ПРИМЕР 3: JOIN запрос (фильмы + жанры)")
    print("=" * 80)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Запрос с JOIN
    query = """
    SELECT m.name, g.name as genre_name, m.rating, m.published
    FROM movies m
    LEFT JOIN genres g ON m.genre_id = g.id
    LIMIT 10;
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        print("\n🎬 Последние 10 фильмов с жанрами:")
        for row in result:
            published_status = "✓" if row[3] else "✗"
            print(f"  Фильм: {row[0]}, Жанр: {row[1]}, Рейтинг: {row[2]}, Опубликовано: {published_status}")

    session.close()


def filter_published_example():
    """Пример фильтрации опубликованных фильмов"""
    print("\n" + "=" * 80)
    print("📰 ПРИМЕР 4: Фильтрация опубликованных фильмов")
    print("=" * 80)

    Session = sessionmaker(bind=engine)
    session = Session()

    # ORM запрос: получить только опубликованные фильмы
    published_movies = session.query(Movie).filter(Movie.published == True).all()

    print(f"\n📺 Найдено опубликованных фильмов: {len(published_movies)}")
    for movie in published_movies[:5]:  # Показываем первые 5
        print(f"  {movie.name} (рейтинг: {movie.rating})")

    session.close()


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("🚀 SQLAlchemy примеры для базы данных 'db_movies'")
    print("=" * 80)

    raw_sql_example()  # Пример 1: Raw SQL
    orm_example()  # Пример 2: ORM
    join_example()  # Пример 3: JOIN
    filter_published_example()  # Пример 4: Фильтрация

    print("\n" + "=" * 80)
    print("✅ Все примеры выполнены!")
    print("=" * 80)