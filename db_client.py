import psycopg2
from psycopg2 import Error
from resources.db_creds import db_creds


def connect_to_postgres():
    """Функция для подключения к PostgreSQL базе данных"""
    connection = None
    cursor = None

    try:
        # Подключение к базе данных с использованием кредов из .env
        connection = psycopg2.connect(**db_creds.get_connection_params())

        print("Подключение успешно установлено")

        # Создание курсора
        cursor = connection.cursor()

        # Вывод информации о PostgreSQL сервере
        print("Информация о сервере PostgreSQL:")
        print(connection.get_dsn_parameters(), "\n")

        # Выполнение SQL-запроса
        cursor.execute("SELECT version();")

        # Получение результата
        record = cursor.fetchone()
        print("Вы подключены к -", record, "\n")

        # Дополнительно: покажем список баз данных
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        print("Доступные базы данных:")
        for db in databases:
            print(f"  - {db[0]}")

    except Error as error:
        print("Ошибка при работе с PostgreSQL:", error)

    finally:
        # Закрытие соединения с базой данных
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Соединение с PostgreSQL закрыто")


if __name__ == "__main__":
    connect_to_postgres()