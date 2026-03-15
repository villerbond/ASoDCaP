"""
Тесты, фиксирующие найденные баги.

"""

import os
import pytest
from bs4 import BeautifulSoup
from src.html_parser import HTMLParser

@pytest.fixture
def parser():
    return HTMLParser()

@pytest.fixture
def avito_path(request):
    cli = request.config.getoption("--avito-html", default=None)
    if cli:
        return cli
    return os.path.join(os.path.dirname(__file__), "../data/avito.html")


# TC-BUG-01: синтетический пример — показывает причину бага
def test_bug01_links_count_synthetic(parser):
    """БАГ #1 — links_count считает <a> без href,
    но extract_links() их пропускает. Метрика не совпадает с реальными данными."""
    html = """<html><body>
        <a href="https://example.com">Link 1</a>
        <a href="/page">Link 2</a>
        <a>No href</a>
    </body></html>"""
    soup = BeautifulSoup(html, "html.parser")

    metrics = parser.get_document_metrics(soup)
    links   = parser.extract_links(soup)

    assert metrics["links_count"] == len(links), (
        f"БАГ #1: metrics={metrics['links_count']}, "
        f"extract_links={len(links)}, "
        f"расхождение={metrics['links_count'] - len(links)}"
    )


# TC-BUG-01b: реальные данные Avito — показывает масштаб бага
def test_bug01_links_count_real_avito(avito_path, parser):
    """БАГ #1 на реальных данных Avito — масштаб расхождения."""
    if not os.path.exists(avito_path):
        pytest.skip(f"Файл не найден: {avito_path}")

    with open(avito_path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    metrics = parser.get_document_metrics(soup)
    links   = parser.extract_links(soup)

    assert metrics["links_count"] == len(links), (
        f"БАГ #1 на Avito: metrics={metrics['links_count']}, "
        f"extract_links={len(links)}, "
        f"расхождение={metrics['links_count'] - len(links)}"
    )