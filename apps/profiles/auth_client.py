import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AuthClientError(Exception):
    """
    Custom exception raised when AUTH_MS communication fails
    """
    pass


class AuthClient:
    """
    Centralized client to communicate with AUTH_MS service.
    Responsible for:
    - Token validation
    - Fetching authenticated user details
    """

    def __init__(self, base_url=None):
        # Base URL of AUTH_MS (remove trailing slash to avoid //)
        self.base_url = (base_url or settings.AUTH_MS_BASE_URL).rstrip("/")

        # Retry strategy for handling temporary failures
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # 2s, 4s, 8s
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )

        # Attach retry adapter
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_user(self, token: str) -> dict:
        """
        Calls AUTH_MS `/me/` endpoint using Bearer token.

        Args:
            token (str): JWT access token

        Returns:
            dict: Authenticated user data

        Raises:
            AuthClientError: For invalid token or connection failure
        """
        if not token:
            raise AuthClientError("Authorization token is missing.")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/me/"

        try:
            response = self.session.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json().get("data")
                if not data:
                    raise AuthClientError("No user data returned from AUTH_MS.")
                return data

            if response.status_code == 401:
                raise AuthClientError("Invalid or expired token.")

            if response.status_code >= 500:
                raise AuthClientError("AUTH_MS is temporarily unavailable.")

            raise AuthClientError(
                f"AUTH_MS returned {response.status_code}: {response.text}"
            )

        except requests.exceptions.Timeout:
            raise AuthClientError("AUTH_MS timed out (cold start possible).")

        except requests.exceptions.RequestException as e:
            raise AuthClientError(f"Error connecting to AUTH_MS: {e}")
