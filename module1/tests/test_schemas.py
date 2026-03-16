"""
Тест-кейсы для schemas.py.
"""
import pytest
from schemas.schemas import (
    product_schema, article_schema, avito_product_schema,
    ALL_SCHEMAS, SCHEMA_NAMES, get_schemas, get_schema_choices
)

class TestSchemaStructure:
    def test_product_schema_has_container(self):
        """TC-SC-01"""
        assert "container" in product_schema
    def test_product_schema_has_fields(self):
        """TC-SC-02"""
        assert {"name", "price", "rating"} == set(product_schema["fields"].keys())
    def test_article_schema_has_container(self):
        """TC-SC-03"""
        assert "container" in article_schema
    def test_article_schema_has_fields(self):
        """TC-SC-04"""
        assert {"title", "author", "date"} == set(article_schema["fields"].keys())
    def test_avito_schema_has_container(self):
        """TC-SC-05"""
        assert "container" in avito_product_schema
    def test_avito_schema_has_fields(self):
        """TC-SC-06"""
        assert {"title", "price", "condition"} == set(avito_product_schema["fields"].keys())

class TestAllSchemas:
    def test_all_schemas_contains_products(self):
        """TC-SC-07"""
        assert "products" in ALL_SCHEMAS
    def test_all_schemas_contains_articles(self):
        """TC-SC-08"""
        assert "articles" in ALL_SCHEMAS
    def test_all_schemas_contains_avito(self):
        """TC-SC-09"""
        assert "avito_products" in ALL_SCHEMAS
    def test_schema_names_contains_all(self):
        """TC-SC-10"""
        assert "all" in SCHEMA_NAMES
    def test_schema_names_contains_known_schemas(self):
        """TC-SC-11"""
        for name in ALL_SCHEMAS:
            assert name in SCHEMA_NAMES

class TestGetSchemas:
    def test_none_returns_all(self):
        """TC-SC-12"""
        result = get_schemas(None)
        assert set(result.keys()) == set(ALL_SCHEMAS.keys())
    def test_all_keyword_returns_all(self):
        """TC-SC-13"""
        result = get_schemas(["all"])
        assert set(result.keys()) == set(ALL_SCHEMAS.keys())
    def test_filter_single_schema(self):
        """TC-SC-14"""
        result = get_schemas(["products"])
        assert list(result.keys()) == ["products"]
    def test_filter_multiple_schemas(self):
        """TC-SC-15"""
        result = get_schemas(["products", "articles"])
        assert set(result.keys()) == {"products", "articles"}
    def test_unknown_name_ignored(self):
        """TC-SC-16"""
        result = get_schemas(["products", "nonexistent"])
        assert "nonexistent" not in result
        assert "products" in result
    def test_returns_copy_not_reference(self):
        """TC-SC-17"""
        result = get_schemas()
        result["injected"] = {}
        assert "injected" not in ALL_SCHEMAS

class TestGetSchemaChoices:
    def test_returns_list(self):
        """TC-SC-18"""
        assert isinstance(get_schema_choices(), list)
    def test_contains_all(self):
        """TC-SC-19"""
        assert "all" in get_schema_choices()
    def test_contains_known_schemas(self):
        """TC-SC-20"""
        choices = get_schema_choices()
        for name in ALL_SCHEMAS:
            assert name in choices
