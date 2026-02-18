import pytest

@pytest.fixture
def context():
    return "https://api.restful-api.dev/objects"

@pytest.fixture
def base_url():
    return{}