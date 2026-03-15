"""
Тест-кейсы для schemas.py.
Покрывает: ALL_SCHEMAS, SCHEMA_NAMES, get_schemas(), get_schema_choices().
"""
import pytest
from schemas.schemas import (
    product_schema, article_schema, avito_product_schema,
    ALL_SCHEMAS, SCHEMA_NAMES, get_schemas, get_schema_choices
)

class TestSchemaStructure:
    def test_product_schema_has_container(self):
        """TC-SC-01: product_schema содержит container"""
        assert "container" in product_schema
    def test_product_schema_has_fields(self):
        """TC-SC-02: product_schema содержит fields name, price, rating"""
        assert {"name", "price", "rating"} == set(product_schema["fields"].keys())
    def test_article_schema_has_container(self):
        """TC-SC-03: article_schema содержит container"""
        assert "container" in article_schema
    def test_article_schema_has_fields(self):
        """TC-SC-04: article_schema содержит fields title, author, date"""
        assert {"title", "author", "date"} == set(article_schema["fields"].keys())
    def test_avito_schema_has_container(self):
        """TC-SC-05: avito_product_schema содержит container"""
        assert "container" in avito_product_schema
    def test_avito_schema_has_fields(self):
        """TC-SC-06: avito_product_schema содержит fields title, price, condition"""
        assert {"title", "price", "condition"} == set(avito_product_schema["fields"].keys())

class TestAllSchemas:
    def test_all_schemas_contains_products(self):
        """TC-SC-07: ALL_SCHEMAS содержит products"""
        assert "products" in ALL_SCHEMAS
    def test_all_schemas_contains_articles(self):
        """TC-SC-08: ALL_SCHEMAS содержит articles"""
        assert "articles" in ALL_SCHEMAS
    def test_all_schemas_contains_avito(self):
        """TC-SC-09: ALL_SCHEMAS содержит avito_products"""
        assert "avito_products" in ALL_SCHEMAS
    def test_schema_names_contains_all(self):
        """TC-SC-10: SCHEMA_NAMES содержит 'all'"""
        assert "all" in SCHEMA_NAMES
    def test_schema_names_contains_known_schemas(self):
        """TC-SC-11: SCHEMA_NAMES содержит все ключи ALL_SCHEMAS"""
        for name in ALL_SCHEMAS:
            assert name in SCHEMA_NAMES

class TestGetSchemas:
    def test_none_returns_all(self):
        """TC-SC-12: get_schemas(None) → все схемы"""
        result = get_schemas(None)
        assert set(result.keys()) == set(ALL_SCHEMAS.keys())
    def test_all_keyword_returns_all(self):
        """TC-SC-13: get_schemas(['all']) → все схемы"""
        result = get_schemas(["all"])
        assert set(result.keys()) == set(ALL_SCHEMAS.keys())
    def test_filter_single_schema(self):
        """TC-SC-14: get_schemas(['products']) → только products"""
        result = get_schemas(["products"])
        assert list(result.keys()) == ["products"]
    def test_filter_multiple_schemas(self):
        """TC-SC-15: get_schemas(['products','articles']) → только они"""
        result = get_schemas(["products", "articles"])
        assert set(result.keys()) == {"products", "articles"}
    def test_unknown_name_ignored(self):
        """TC-SC-16: неизвестное имя схемы игнорируется"""
        result = get_schemas(["products", "nonexistent"])
        assert "nonexistent" not in result
        assert "products" in result
    def test_returns_copy_not_reference(self):
        """TC-SC-17: get_schemas возвращает копию, не ссылку на ALL_SCHEMAS"""
        result = get_schemas()
        result["injected"] = {}
        assert "injected" not in ALL_SCHEMAS

class TestGetSchemaChoices:
    def test_returns_list(self):
        """TC-SC-18: get_schema_choices() возвращает список"""
        assert isinstance(get_schema_choices(), list)
    def test_contains_all(self):
        """TC-SC-19: список содержит 'all'"""
        assert "all" in get_schema_choices()
    def test_contains_known_schemas(self):
        """TC-SC-20: список содержит все имена схем"""
        choices = get_schema_choices()
        for name in ALL_SCHEMAS:
            assert name in choices
