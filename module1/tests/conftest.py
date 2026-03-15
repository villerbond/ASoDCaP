import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def pytest_addoption(parser):
    parser.addoption(
        "--avito-html",
        action="store",
        default=None,
        help="Путь к HTML файлу Avito для интеграционных тестов"
    )