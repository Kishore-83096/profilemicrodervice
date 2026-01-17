# apps/profiles/auth_client.py
import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AuthClientError(Exception):
    """Custom exception for AuthClient errors"""
    pass


class AuthClient:
    """
    Central client for communicating with AUTH_MS.
    Handles token validation and fetching user info.
    """

    def __init__(self, base_url=None):
        # Remove trailing slash to avoid double slashes
        self.base_url = (base_url or settings.AUTH_MS_BASE_URL).rstrip("/")

        # ---- Retry configuration ----
        retry_strategy = Retry(
            total=3,                    # total retry attempts
            backoff_factor=2,           # 2s, 4s, 8s delays
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_user(self, token: str) -> dict:
        """
        Calls AUTH_MS /me endpoint with the provided token.
        Returns user info JSON if valid.
        Raises AuthClientError if token is missing, invalid, or AUTH_MS is unreachable.
        """
        if not token:
            raise AuthClientError("Authorization token is missing.")

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}/me/"

        print("Sending token to AUTH_MS:", headers)  # DEBUG
        print("AUTH_MS URL:", url)  # DEBUG

        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=30   # enough for Render cold start
            )

            if response.status_code == 200:
                return response.json()

            elif response.status_code == 401:
                raise AuthClientError("Invalid or expired token.")

            elif response.status_code >= 500:
                raise AuthClientError(
                    "AUTH_MS is temporarily unavailable. Please try again."
                )

            else:
                raise AuthClientError(
                    f"AUTH_MS returned status {response.status_code}: {response.text}"
                )

        except requests.exceptions.Timeout:
            raise AuthClientError("AUTH_MS timed out (possible cold start).")

        except requests.exceptions.RequestException as e:
            raise AuthClientError(f"Error connecting to AUTH_MS: {e}")
