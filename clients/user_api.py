from custom_requester.custom_requester import CustomRequester
from constants import BASE_AUTH_URL, USER_ENDPOINT
from entities.api_models import BaseModel, User


class UserAPI(CustomRequester):
    """Класс для работы с API пользователей"""

    def __init__(self, session):
        super().__init__(
            session=session,
            base_url=BASE_AUTH_URL
        )

    def create_user(self, user_data: dict | BaseModel, expected_status: int = 201):
        """
        Создание пользователя.

        :param user_data: dict или UserCreate модель
        :param expected_status: Ожидаемый статус-код (по умолчанию 201)
        """
        if isinstance(user_data, BaseModel):
            user_data = user_data.model_dump(mode='json', exclude_none=True)

        return self.send_request(
            method="POST",
            endpoint="/user",
            data=user_data,
            expected_status=expected_status
        )

    def get_user(self, user_id, expected_status=200):
        """Получение информации о пользователе"""
        return self.send_request(
            method="GET",
            endpoint=f"{USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )

    def update_user(self, user_id, update_data, expected_status=200):
        """Обновление пользователя (PATCH)"""
        return self.send_request(
            method="PATCH",
            endpoint=f"{USER_ENDPOINT}/{user_id}",
            data=update_data,
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        """Удаление пользователя"""
        return self.send_request(
            method="DELETE",
            endpoint=f"{USER_ENDPOINT}/{user_id}",
            expected_status=expected_status
        )