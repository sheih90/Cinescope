from enum import Enum

class Roles(Enum):
    """Перечисление ролей пользователей в системе"""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"