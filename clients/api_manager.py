
from clients.auth_api import AuthAPI
from clients.user_api import UserAPI
from clients.movies_api import MoviesAPI


class ApiManager:
    """Класс для управления API-классами с единой HTTP-сессией"""

    def __init__(self, session):
        """
        Инициализация ApiManager.
        :param session: HTTP-сессия, используемая всеми API-классами.
        """
        self.session = session
        self.auth = AuthAPI(session)      # auth.register_user(...)
        self.user = UserAPI(session)      # user.get_user_info(...)
        self.movies = MoviesAPI(session)

    def close_session(self):
        self.session.close()