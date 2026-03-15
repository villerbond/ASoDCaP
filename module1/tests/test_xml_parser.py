"""
Тест-кейсы для XMLParser.
Покрывает: parse, extract_elements.
"""

import pytest
from src.xml_parser import XMLParser


@pytest.fixture
def parser():
    return XMLParser()

@pytest.fixture
def simple_xml():
    return """<?xml version="1.0"?>
<catalog>
  <book id="1">
    <title>Python Basics</title>
    <author>Alice</author>
    <price>29.99</price>
  </book>
  <book id="2">
    <title>Advanced Python</title>
    <author>Bob</author>
    <price>49.99</price>
  </book>
</catalog>"""

@pytest.fixture
def single_tag_xml():
    return "<root><child>Text</child></root>"


# ===========================================================================
# TC-XP-01  Инициализация
# ===========================================================================

class TestXMLParserInit:

    def test_parser_type(self, parser):
        """TC-XP-01: parser_type установлен в 'xml'"""
        assert parser.parser_type == "xml"


# ===========================================================================
# TC-XP-02..06  parse
# ===========================================================================

class TestXMLParse:

    def test_root_name(self, parser, simple_xml):
        """TC-XP-02: корневой тег определяется верно"""
        result = parser.parse(simple_xml)
        assert result["root"] == "catalog"

    def test_elements_key_present(self, parser, simple_xml):
        """TC-XP-03: результат содержит ключ elements"""
        result = parser.parse(simple_xml)
        assert "elements" in result

    def test_elements_is_list(self, parser, simple_xml):
        """TC-XP-04: elements — список"""
        result = parser.parse(simple_xml)
        assert isinstance(result["elements"], list)

    def test_elements_not_empty(self, parser, simple_xml):
        """TC-XP-05: elements не пуст для непустого XML"""
        result = parser.parse(simple_xml)
        assert len(result["elements"]) > 0

    def test_single_root_tag(self, parser, single_tag_xml):
        """TC-XP-06: работает с минимальным XML (root + один дочерний тег)"""
        result = parser.parse(single_tag_xml)
        assert result["root"] == "root"


# ===========================================================================
# TC-XP-07..11  extract_elements
# ===========================================================================

class TestExtractElements:

    def test_element_has_tag_key(self, parser, simple_xml):
        """TC-XP-07: каждый элемент содержит ключ 'tag'"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(simple_xml, "xml")
        elements = parser.extract_elements(soup)
        assert all("tag" in el for el in elements)

    def test_element_has_text_key(self, parser, simple_xml):
        """TC-XP-08: каждый элемент содержит ключ 'text'"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(simple_xml, "xml")
        elements = parser.extract_elements(soup)
        assert all("text" in el for el in elements)

    def test_known_tag_present(self, parser, simple_xml):
        """TC-XP-09: тег 'title' присутствует в элементах"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(simple_xml, "xml")
        elements = parser.extract_elements(soup)
        tags = [el["tag"] for el in elements]
        assert "title" in tags

    def test_text_extracted(self, parser, simple_xml):
        """TC-XP-10: текст внутри тега извлекается корректно"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(simple_xml, "xml")
        elements = parser.extract_elements(soup)
        texts = [el["text"] for el in elements]
        assert "Python Basics" in texts

    def test_nested_tags_included(self, parser, simple_xml):
        """TC-XP-11: вложенные теги (book, title, author) все включены"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(simple_xml, "xml")
        elements = parser.extract_elements(soup)
        tags = {el["tag"] for el in elements}
        assert {"book", "title", "author", "price"}.issubset(tags)
