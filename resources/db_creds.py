
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


class DBCreds:
    """Класс для хранения кредов подключения к БД"""

    def __init__(self):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")

    def get_connection_params(self) -> dict:
        """Возвращает параметры подключения в виде dict"""
        return {
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port
        }

    def __repr__(self):
        return f"DB_Creds(dbname={self.dbname}, user={self.user}, host={self.host})"


# Создаём глобальный экземпляр для удобного импорта
db_creds = DBCreds()


class MoviesDbCreds:
    """Класс для хранения кредов подключения к db_movies"""

    HOST = os.getenv('DB_MOVIES_HOST', 'localhost')
    PORT = os.getenv('DB_MOVIES_PORT', '5432')
    DATABASE_NAME = os.getenv('DB_MOVIES_NAME')
    USERNAME = os.getenv('DB_MOVIES_USERNAME', 'postgres')
    PASSWORD = os.getenv('DB_MOVIES_PASSWORD')

    @classmethod
    def get_connection_string(cls) -> str:
        """Возвращает connection string для SQLAlchemy"""
        return (
            f"postgresql+psycopg2://{cls.USERNAME}:{cls.PASSWORD}"
            f"@{cls.HOST}:{cls.PORT}/{cls.DATABASE_NAME}"
        )

    @classmethod
    def get_connection_params(cls) -> dict:
        """Возвращает параметры для psycopg2"""
        return {
            "dbname": cls.DATABASE_NAME,
            "user": cls.USERNAME,
            "password": cls.PASSWORD,
            "host": cls.HOST,
            "port": cls.PORT
        }

    def __repr__(self):
        return f"MoviesDbCreds(db={cls.DATABASE_NAME}, host={cls.HOST})"


# Глобальный экземпляр для удобного импорта
movies_db_creds = MoviesDbCreds()