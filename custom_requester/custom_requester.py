
import json
import requests
import logging
import os
from pydantic import BaseModel
from constants import RED, GREEN, RESET

class CustomRequester:
    """Базовый класс для отправки HTTP-запросов с логированием"""

    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session: requests.Session = None, base_url: str = "", base_headers: dict = None):

        self.base_url = base_url
        self.base_headers = base_headers or {}

        # Если передана сессия — используем её, иначе создаём новую
        if session:
            self.session = session
        else:
            self.session = requests.Session()

        self.session.headers.update(self.base_headers)

        self.logger = logging.getLogger(__name__)

    def send_request(
            self,
            method: str,
            endpoint: str,
            data=None,
            params=None,
            expected_status: int = 200,
            need_logging: bool = True
    ):
        """
        Универсальный метод отправки запросов.

        :param  dict или Pydantic BaseModel
        """
        url = f"{self.base_url}{endpoint}"
        if isinstance(data, BaseModel):
            data = data.model_dump(mode='json', exclude_unset=True)

        response = self.session.request(
            method,
            url,
            json=data,
            params=params
        )

        self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise ValueError(f"Unexpected status code: {response.status_code}. Expected: {expected_status}")

        return response

    def _update_session_headers(self, **kwargs):
        """
        Обновление заголовков сессии.
        :param kwargs: Дополнительные заголовки.
        """
        self.headers.update(kwargs)  # Обновляем базовые заголовки
        self.session.headers.update(self.headers)  # Обновляем заголовки в текущей сессии

    def log_request_and_response(self, response):
        """Логирование запросов и ответов"""
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text

            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not is_success:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response_status}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")
