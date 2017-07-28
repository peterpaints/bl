import os
import pytest

from api import create_app


config_name = os.getenv('APP_SETTINGS')


@pytest.fixture
def app():
    app = create_app(config_name)
    return app
