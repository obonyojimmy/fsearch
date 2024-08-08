# conftest.py

import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--fsearch-config", action="store", default=None, help="Path to the configuration file for fsearch"
    )

@pytest.fixture
def config_file_path(request):
    return request.config.getoption("--fsearch-config")

@pytest.fixture(scope="class")
def config_file_cls(request):
    request.cls.config_file = request.config.getoption("--fsearch-config")
