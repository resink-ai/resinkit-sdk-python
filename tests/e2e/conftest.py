import os
import time

import pytest
import requests
from dotenv import load_dotenv

DEFAULT_RSK_API_URL = "http://localhost:8603"


def is_service_up(url: str, max_retries: int = 3, retry_delay: int = 1) -> bool:
    """Check if the service is running by making a request to the health endpoint"""
    for _ in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(retry_delay)
    return False


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables before any tests run"""
    load_dotenv()
    # Set default BASE_URL if not provided in .env
    if not os.getenv("BASE_URL"):
        os.environ["BASE_URL"] = DEFAULT_RSK_API_URL


@pytest.fixture(scope="session", autouse=True)
def check_service():
    """Check if the service is running before running tests"""
    service_url = os.getenv("BASE_URL", DEFAULT_RSK_API_URL)
    if not is_service_up(service_url):
        pytest.skip(
            f"Service is not running at {service_url}. Please start the service before running the tests."
        )
