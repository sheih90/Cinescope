from db_requester.db_client import get_db_session, execute_raw_query
from db_models import Genre, MovieDBModel, UserDBModel
import time


def test_raw_query():
    """Тест сырого SQL-запроса"""
    print("\n🔍 Тест: Raw SQL запрос")

    query = "SELECT id, name FROM genres LIMIT 5;"
    results = execute_raw_query(query)

    for row in results:
        print(f"  ID: {row[0]}, Название: {row[1]}")


def test_orm_query():
    """Тест ORM-запроса"""
    print("\n🔍 Тест: ORM запрос")

    session = get_db_session()

    # SELECT
    genres = session.query(Genre).all()
    print(f"  Найдено жанров: {len(genres)}")

    # INSERT
    new_genre = Genre(name="Тестовый жанр")
    session.add(new_genre)
    session.commit()
    print(f"  ✅ Добавлен жанр с ID: {new_genre.id}")

    # UPDATE
    genre = session.query(Genre).filter(Genre.id == new_genre.id).first()
    if genre:
        genre.name = "Обновлённый жанр"
        session.commit()
        print(f"  ✅ Обновлён: {genre.name}")

    # DELETE
    session.delete(genre)
    session.commit()
    print(f"  ✅ Удалён жанр ID: {new_genre.id}")

    session.close()


def test_movies_with_genres():
    """Тест JOIN-запроса"""
    print("\n🔍 Тест: Фильмы с жанрами (JOIN)")

    query = """
    SELECT m.name, g.name as genre_name, m.rating
    FROM movies m
    LEFT JOIN genres g ON m.genre_id = g.id
    WHERE m.published = :published
    LIMIT 5;
    """

    results = execute_raw_query(query, {"published": True})

    for row in results:
        print(f"  🎬 {row[0]} | Жанр: {row[1]} | Рейтинг: {row[2]}")


def test_users_query():
    """Тест запроса к таблице users"""
    print("\n🔍 Тест: Запрос к users")

    session = get_db_session()

    # SELECT - получить первых 5 пользователей
    users = session.query(UserDBModel).limit(5).all()
    print(f"  Найдено пользователей: {len(users)}")

    for user in users:
        print(f"  👤 {user.email} | Verified: {user.verified} | Roles: {user.roles}")

    # SELECT с фильтром
    verified_users = session.query(UserDBModel).filter(
        UserDBModel.verified == True
    ).limit(3).all()

    print(f"\n  ✅ Verified пользователей: {len(verified_users)}")

    session.close()


def test_user_by_id():
    """Тест поиска пользователя по ID"""
    print("\n🔍 Тест: Поиск пользователя по ID")

    session = get_db_session()

    # Вставь реальный ID пользователя из твоей БД
    user_id = "3a172562-e05d-4768-82dd-a098d8e7bbb3"  # ← Замени на свой!

    user = session.query(UserDBModel).filter(UserDBModel.id == user_id).first()

    if user:
        print(f"  👤 Найден пользователь:")
        print(f"     Email: {user.email}")
        print(f"     Full Name: {user.full_name}")
        print(f"     Verified: {user.verified}")
        print(f"     Roles: {user.roles}")
    else:
        print(f"  ❌ Пользователь с ID {user_id} не найден")
        print(f"  💡 Подсказка: выполни SELECT id FROM users LIMIT 1 в DBeaver")

    session.close()


def test_movies_query():
    """Тест запроса к таблице movies"""
    print("\n🔍 Тест: Запрос к movies")

    session = get_db_session()

    # SELECT - получить первые 5 фильмов
    movies = session.query(MovieDBModel).limit(5).all()
    print(f"  Найдено фильмов: {len(movies)}")

    for movie in movies:
        published_status = "✓" if movie.published else "✗"
        print(f"  🎬 {movie.name} | Рейтинг: {movie.rating} | Опубликовано: {published_status}")

    # SELECT с фильтром - только опубликованные
    published_movies = session.query(MovieDBModel).filter(
        MovieDBModel.published == True,
        MovieDBModel.rating > 0
    ).limit(3).all()

    print(f"\n  ✅ Опубликованных фильмов с рейтингом > 0: {len(published_movies)}")

    session.close()


def test_movie_with_genre():
    """Тест получения фильма с жанром (JOIN через ORM)"""
    print("\n🔍 Тест: Фильм с жанром (ORM JOIN)")

    session = get_db_session()

    # Получаем фильмы с подгруженным жанром
    movies = session.query(MovieDBModel).limit(3).all()

    for movie in movies:
        genre_name = movie.genre.name if movie.genre else "Без жанра"
        print(f"  🎬 {movie.name}")
        print(f"     Жанр: {genre_name}")
        print(f"     Рейтинг: {movie.rating}")
        print(f"     Цена: {movie.price} руб.")

    session.close()


def test_movie_crud():
    """Тест CRUD операций с фильмами"""
    print("\n🔍 Тест: CRUD операции с фильмами")

    session = get_db_session()

    # === CREATE ===
    print("\n  ➕ Добавляем тестовый фильм:")

    # Генерируем уникальное имя с таймстампом
    test_name = f"Тестовый фильм {int(time.time())}"

    new_movie = MovieDBModel(
        name=test_name,  # уникальное имя
        description="Описание тестового фильма",
        price=100,
        rating=7.5,
        published=False,
        genre_id=1,
        location="MSK",  # MSK или SPB (ENUM значения)
        image_url="https://example.com/image.jpg"
    )
    session.add(new_movie)
    session.commit()
    print(f"     ✅ Добавлен фильм с ID: {new_movie.id}")

    # === READ ===
    print("\n  📖 Читаем добавленный фильм:")
    movie = session.query(MovieDBModel).filter(MovieDBModel.id == new_movie.id).first()
    if movie:
        print(f"     Название: {movie.name}")
        print(f"     Рейтинг: {movie.rating}")
        print(f"     Локация: {movie.location}")
        print(f"     Опубликовано: {movie.published}")

    # === UPDATE ===
    print("\n  ✏️ Обновляем фильм:")
    movie.rating = 8.0
    movie.published = True
    session.commit()
    print(f"     ✅ Обновлён: рейтинг={movie.rating}, published={movie.published}")

    # === DELETE ===
    print("\n  🗑️ Удаляем фильм:")
    session.delete(movie)
    session.commit()
    print(f"     ✅ Удалён фильм ID: {new_movie.id}")

    session.close()


if __name__ == "__main__":
    print("🚀 Тесты подключения к БД")
    print("=" * 60)

    test_raw_query()
    test_orm_query()
    test_movies_with_genres()
    test_users_query()
    test_user_by_id()
    test_movies_query()
    test_movie_with_genre()
    test_movie_crud()

    print("\n" + "=" * 60)
    print("✅ Все тесты выполнены!")  # ← Без лишних пробелов в начале!