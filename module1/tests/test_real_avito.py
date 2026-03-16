"""
Тесты на реальных данных (avito.html)
"""

import os
import pytest
from src.html_parser import HTMLParser
from src.parser_manager import ParserManager

def extract_avito_items(html: str) -> list:
    """
    Извлекает карточки объявлений из HTML страницы Avito.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for el in soup.find_all(attrs={"data-marker": "item"}):
        title  = el.find(attrs={"data-marker": "item-title"})
        price  = el.find(attrs={"data-marker": "item-price-value"})
        params = el.find(attrs={"data-marker": "item-specific-params"})
        loc    = el.find(attrs={"data-marker": "item-location"})
        link   = el.find("a", attrs={"data-marker": "item-title"})
        img    = el.find("img")

        items.append({
            "title":     title.get_text(strip=True) if title else None,
            "price":     price.get_text(strip=True) if price else None,
            "condition": params.get_text(strip=True) if params else None,
            "location":  loc.get_text(strip=True) if loc else None,
            "link":      f"https://avito.ru{link.get('href')}" if link else None,
            "img":       img.get("src", "") if img else None,
        })

    return items


# ─── фикстуры ────────────────────────────────────────────────────────────────

def get_avito_path(request):
    cli = request.config.getoption("--avito-html", default=None)
    if cli:
        return cli
    return os.path.join(os.path.dirname(__file__), "../data/avito.html")

@pytest.fixture
def avito_path(request):
    return get_avito_path(request)

@pytest.fixture
def avito_html(avito_path):
    with open(avito_path, encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def avito_items(avito_html):
    return extract_avito_items(avito_html)

@pytest.fixture
def parser():
    return HTMLParser()

@pytest.fixture
def manager():
    return ParserManager()


# ─── skip если файл не найден ────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "avito: тесты на реальных данных Avito"
    )

@pytest.fixture(autouse=True)
def skip_if_no_file(request, avito_path):
    if not os.path.exists(avito_path):
        pytest.skip(f"Файл не найден: {avito_path}. "
                    f"Передай путь через --avito-html=<путь>")


# ============================================================================
# TC-AV-01..05  Базовая структура страницы
# ============================================================================

class TestAvitoPageStructure:

    def test_page_parses_without_error(self, manager, avito_path):
        """TC-AV-01"""
        result = manager.process_file(avito_path)
        assert result is not None

    def test_page_has_title(self, manager, avito_path):
        """TC-AV-02"""
        result = manager.process_file(avito_path)
        assert result["metadata"]["title"] is not None
        assert "Авито" in result["metadata"]["title"] or "avito" in result["metadata"]["title"].lower()

    def test_page_has_links(self, manager, avito_path):
        """TC-AV-03"""
        result = manager.process_file(avito_path)
        assert result["metrics"]["links_count"] > 0

    def test_page_has_images(self, manager, avito_path):
        """TC-AV-04"""
        result = manager.process_file(avito_path)
        assert result["metrics"]["images_count"] > 0

    def test_metrics_match_extracted_data(self, manager, avito_path):
        """TC-AV-05"""
        result = manager.process_file(avito_path)
        assert result["metrics"]["images_count"] == len(result["images"])
        assert result["metrics"]["links_count"] == len(result["links"])


# ============================================================================
# TC-AV-06..10  Карточки объявлений
# ============================================================================

class TestAvitoItems:

    def test_items_found(self, avito_items):
        """TC-AV-06"""
        assert len(avito_items) > 0

    def test_items_count_reasonable(self, avito_items):
        """TC-AV-07"""
        assert 1 <= len(avito_items) <= 200

    def test_every_item_has_title(self, avito_items):
        """TC-AV-08"""
        for item in avito_items:
            assert item["title"] is not None, f"Нет title у карточки: {item}"

    def test_every_item_has_price(self, avito_items):
        """TC-AV-09"""
        for item in avito_items:
            assert item["price"] is not None, f"Нет price у карточки: {item}"

    def test_every_item_has_link(self, avito_items):
        """TC-AV-10"""
        for item in avito_items:
            assert item["link"] is not None, f"Нет link у карточки: {item}"


# ============================================================================
# TC-AV-11..15  Качество данных
# ============================================================================

class TestAvitoDataQuality:

    def test_prices_contain_ruble_sign(self, avito_items):
        """TC-AV-11"""
        prices_with_currency = [
            i for i in avito_items
            if i["price"] and ("₽" in i["price"] or "руб" in i["price"])
        ]
        assert len(prices_with_currency) > 0

    def test_links_point_to_avito(self, avito_items):
        """TC-AV-12"""
        for item in avito_items:
            if item["link"]:
                assert "avito.ru" in item["link"], \
                    f"Ссылка не на avito.ru: {item['link']}"

    def test_images_have_url(self, avito_items):
        """TC-AV-13"""
        items_with_img = [i for i in avito_items if i["img"]]
        assert len(items_with_img) > 0

    def test_condition_values_known(self, avito_items):
        """TC-AV-14"""
        known = {"Новый", "Б/у", "Б⁠/⁠у"}
        items_with_condition = [i for i in avito_items if i["condition"]]
        for item in items_with_condition:
            cond = item["condition"]
            assert any(k in cond for k in known), \
                f"Неизвестное состояние: {cond!r}"

    def test_no_duplicate_links(self, avito_items):
        """TC-AV-15"""
        links = [i["link"] for i in avito_items if i["link"]]
        assert len(links) == len(set(links)), "Найдены дублирующиеся ссылки"
