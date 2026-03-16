"""
Тест-кейсы для HTMLParser
"""
import pytest
from src.html_parser import HTMLParser

@pytest.fixture
def parser():
    return HTMLParser()

@pytest.fixture
def full_html():
    return """<!DOCTYPE html>
<html>
<head>
  <title>Test Page</title>
  <meta name="description" content="Test description">
  <meta name="keywords" content="test, parser">
</head>
<body>
  <h1>Main Heading</h1><h2>Sub Heading</h2><h3>Sub Sub Heading</h3>
  <p>First paragraph.</p><p>Second paragraph.</p>
  <a href="https://example.com">Example</a><a href="/relative">Relative</a>
  <img src="image.jpg" alt="Test image"><img src="no-alt.png">
  <table>
    <tr><th>Name</th><th>Price</th></tr>
    <tr><td>Apple</td><td>1.00</td></tr>
    <tr><td>Banana</td><td>0.50</td></tr>
  </table>
  <ul><li>Item A</li><li>Item B</li></ul>
  <ol><li>Step 1</li><li>Step 2</li></ol>
</body>
</html>"""

@pytest.fixture
def soup(full_html, parser):
    from bs4 import BeautifulSoup
    return BeautifulSoup(full_html, parser.parser_type)

@pytest.fixture
def product_html():
    return """<html><body>
  <div class="product"><h2>Widget</h2><span class="price">9.99</span><span class="rating">4.5</span></div>
  <div class="product"><h2>Gadget</h2><span class="price">19.99</span></div>
</body></html>"""

@pytest.fixture
def article_html():
    return """<html><body>
  <article><h2>Breaking News</h2><span class="author">John Doe</span><span class="date">2024-01-01</span></article>
</body></html>"""

class TestValidateHtml:
    def test_valid_html_passes(self, parser, full_html):
        """TC-HP-01"""
        parser.validate_html(full_html)
    def test_empty_string_raises(self, parser):
        """TC-HP-02"""
        with pytest.raises(ValueError, match="empty"):
            parser.validate_html("")
    def test_whitespace_only_raises(self, parser):
        """TC-HP-03"""
        with pytest.raises(ValueError, match="empty"):
            parser.validate_html("   \n\t  ")
    def test_plain_text_raises(self, parser):
        """TC-HP-04"""
        with pytest.raises(ValueError, match="Invalid HTML structure"):
            parser.validate_html("Just some plain text")
    def test_minimal_div_passes(self, parser):
        """TC-HP-05"""
        parser.validate_html("<div>ok</div>")

class TestExtractMetadata:
    def test_title_extracted(self, parser, soup):
        """TC-HP-06"""
        assert parser.extract_metadata(soup)["title"] == "Test Page"
    def test_description_extracted(self, parser, soup):
        """TC-HP-07"""
        assert parser.extract_metadata(soup)["description"] == "Test description"
    def test_keywords_extracted(self, parser, soup):
        """TC-HP-08"""
        assert parser.extract_metadata(soup)["keywords"] == "test, parser"
    def test_no_title_returns_none(self, parser):
        """TC-HP-09"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body></body></html>", "html.parser")
        assert parser.extract_metadata(s)["title"] is None
    def test_no_meta_tags_returns_none(self, parser):
        """TC-HP-10"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><head><title>X</title></head></html>", "html.parser")
        meta = parser.extract_metadata(s)
        assert meta["description"] is None and meta["keywords"] is None

class TestExtractHeadings:
    def test_h1_extracted(self, parser, soup):
        """TC-HP-11"""
        assert "Main Heading" in parser.extract_headings(soup)["h1"]
    def test_h2_extracted(self, parser, soup):
        """TC-HP-12"""
        assert "Sub Heading" in parser.extract_headings(soup)["h2"]
    def test_all_levels_present(self, parser, soup):
        """TC-HP-13"""
        h = parser.extract_headings(soup)
        for i in range(1, 7): assert f"h{i}" in h
    def test_missing_level_returns_empty_list(self, parser, soup):
        """TC-HP-14"""
        assert parser.extract_headings(soup)["h4"] == []
    def test_empty_heading_not_included(self, parser):
        """TC-HP-15"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body><h1>  </h1><h1>Real</h1></body></html>", "html.parser")
        assert parser.extract_headings(s)["h1"] == ["Real"]

class TestExtractParagraphs:
    def test_paragraphs_count(self, parser, soup):
        """TC-HP-16"""
        assert len(parser.extract_paragraphs(soup)) == 2
    def test_paragraph_text(self, parser, soup):
        """TC-HP-17"""
        assert "First paragraph." in parser.extract_paragraphs(soup)
    def test_empty_paragraph_excluded(self, parser):
        """TC-HP-18"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body><p></p><p>Text</p></body></html>", "html.parser")
        assert parser.extract_paragraphs(s) == ["Text"]

class TestExtractLinks:
    def test_links_count(self, parser, soup):
        """TC-HP-19"""
        assert len(parser.extract_links(soup)) == 2
    def test_link_url(self, parser, soup):
        """TC-HP-20"""
        assert "https://example.com" in [l["url"] for l in parser.extract_links(soup)]
    def test_link_text(self, parser, soup):
        """TC-HP-21"""
        assert "Example" in [l["text"] for l in parser.extract_links(soup)]
    def test_anchor_without_href_gets_hash(self, parser):
        """TC-HP-22"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body><a>No href</a></body></html>", "html.parser")
        links = parser.extract_links(s)
        assert len(links) == 1
        assert links[0]["url"] == "#"

class TestExtractImages:
    def test_images_count(self, parser, soup):
        """TC-HP-23"""
        assert len(parser.extract_images(soup)) == 2
    def test_image_src(self, parser, soup):
        """TC-HP-24"""
        assert "image.jpg" in [i["src"] for i in parser.extract_images(soup)]
    def test_image_alt_default_empty(self, parser, soup):
        """TC-HP-25"""
        no_alt = next(i for i in parser.extract_images(soup) if i["src"] == "no-alt.png")
        assert no_alt["alt"] == ""
    def test_image_without_src_excluded(self, parser):
        """TC-HP-26"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body><img alt='x'></body></html>", "html.parser")
        assert parser.extract_images(s) == []

class TestExtractTables:
    def test_table_count(self, parser, soup):
        """TC-HP-27"""
        assert len(parser.extract_tables(soup)) == 1
    def test_table_headers(self, parser, soup):
        """TC-HP-28"""
        assert parser.extract_tables(soup)[0]["headers"] == ["Name", "Price"]
    def test_table_rows(self, parser, soup):
        """TC-HP-29"""
        assert ["Apple", "1.00"] in parser.extract_tables(soup)[0]["rows"]
    def test_table_row_count(self, parser, soup):
        """TC-HP-30"""
        assert parser.extract_tables(soup)[0]["row_count"] == 2

class TestExtractLists:
    def test_unordered_list(self, parser, soup):
        """TC-HP-31"""
        assert ["Item A", "Item B"] in parser.extract_lists(soup)["unordered"]
    def test_ordered_list(self, parser, soup):
        """TC-HP-32"""
        assert ["Step 1", "Step 2"] in parser.extract_lists(soup)["ordered"]
    def test_empty_list_excluded(self, parser):
        """TC-HP-33"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup("<html><body><ul></ul></body></html>", "html.parser")
        assert parser.extract_lists(s)["unordered"] == []
    def test_both_keys_always_present(self, parser, soup):
        """TC-HP-34"""
        lsts = parser.extract_lists(soup)
        assert "unordered" in lsts and "ordered" in lsts

class TestExtractStructuredBlocks:
    def test_products_count(self, parser, product_html):
        """TC-HP-35"""
        from bs4 import BeautifulSoup
        from schemas.schemas import product_schema
        assert len(parser.extract_structured_blocks(BeautifulSoup(product_html, "html.parser"), product_schema)) == 2
    def test_product_name(self, parser, product_html):
        """TC-HP-36"""
        from bs4 import BeautifulSoup
        from schemas.schemas import product_schema
        names = [r["name"] for r in parser.extract_structured_blocks(BeautifulSoup(product_html, "html.parser"), product_schema)]
        assert "Widget" in names
    def test_missing_field_returns_none(self, parser, product_html):
        """TC-HP-37"""
        from bs4 import BeautifulSoup
        from schemas.schemas import product_schema
        results = parser.extract_structured_blocks(BeautifulSoup(product_html, "html.parser"), product_schema)
        assert next(r for r in results if r["name"] == "Gadget")["rating"] is None
    def test_article_schema(self, parser, article_html):
        """TC-HP-38"""
        from bs4 import BeautifulSoup
        from schemas.schemas import article_schema
        results = parser.extract_structured_blocks(BeautifulSoup(article_html, "html.parser"), article_schema)
        assert results[0]["title"] == "Breaking News"
        assert results[0]["author"] == "John Doe"
    def test_no_container_returns_empty(self, parser, soup):
        """TC-HP-39"""
        assert parser.extract_structured_blocks(soup, {}) == []
    def test_whitespace_cleaned_in_text(self, parser):
        """TC-HP-39b: лишние пробелы очищаются через join/split"""
        from bs4 import BeautifulSoup
        from schemas.schemas import product_schema
        html = '<html><body><div class="product"><h2>My   Widget</h2><span class="price">9.99</span></div></body></html>'
        results = parser.extract_structured_blocks(BeautifulSoup(html, "html.parser"), product_schema)
        assert results[0]["name"] == "My Widget"

class TestGetDocumentMetrics:
    def test_links_count_metric(self, parser, soup):
        """TC-HP-40"""
        assert parser.get_document_metrics(soup)["links_count"] == 2
    def test_images_count_metric(self, parser, soup):
        """TC-HP-41"""
        assert parser.get_document_metrics(soup)["images_count"] == 2
    def test_paragraphs_count_metric(self, parser, soup):
        """TC-HP-42"""
        assert parser.get_document_metrics(soup)["paragraphs_count"] == 2
    def test_headings_count_metric(self, parser, soup):
        """TC-HP-43"""
        assert parser.get_document_metrics(soup)["headings_count"] == 3
    def test_tables_count_metric(self, parser, soup):
        """TC-HP-44"""
        assert parser.get_document_metrics(soup)["tables_count"] == 1
    def test_lists_count_metric(self, parser, soup):
        """TC-HP-45"""
        assert parser.get_document_metrics(soup)["lists_count"] == 2

class TestBuildDomTree:
    def test_root_tag(self, parser, soup):
        """TC-HP-46"""
        assert parser.build_dom_tree(soup.find("html"))["tag"] == "html"
    def test_children_present(self, parser, soup):
        """TC-HP-47"""
        assert len(parser.build_dom_tree(soup.find("html"))["children"]) > 0
    def test_none_input_returns_none(self, parser):
        """TC-HP-48"""
        assert parser.build_dom_tree(None) is None
    def test_attributes_captured(self, parser):
        """TC-HP-49"""
        from bs4 import BeautifulSoup
        s = BeautifulSoup('<html><body><a href="x">link</a></body></html>', "html.parser")
        tree = parser.build_dom_tree(s.find("html"))
        assert tree["children"][0]["children"][0]["attributes"] == {"href": "x"}

class TestVisualizeDomTree:
    def test_runs_without_error(self, parser, soup, capsys):
        """TC-HP-50"""
        parser.visualize_dom_tree(parser.build_dom_tree(soup.find("html")))
        assert "<html>" in capsys.readouterr().out

class TestParseCommonData:
    def test_all_true_returns_all_sections(self, parser, soup):
        """TC-HP-51"""
        data = parser._parse_common_data(soup, {"all": True})
        for key in ["metadata","headings","paragraphs","links","images","tables","lists","metrics","dom_tree"]:
            assert key in data
    def test_data_types_headings_only(self, parser, soup):
        """TC-HP-52"""
        data = parser._parse_common_data(soup, {"all": False, "data_types": ["headings"]})
        assert "headings" in data
        assert "metadata" not in data
    def test_data_types_multiple(self, parser, soup):
        """TC-HP-53"""
        data = parser._parse_common_data(soup, {"all": False, "data_types": ["links", "images"]})
        assert "links" in data and "images" in data
        assert "headings" not in data
    def test_dom_type_returns_dom_tree(self, parser, soup):
        """TC-HP-54"""
        data = parser._parse_common_data(soup, {"all": False, "data_types": ["dom"]})
        assert "dom_tree" in data and "headings" not in data
    def test_empty_options_returns_empty(self, parser, soup):
        """TC-HP-55"""
        assert parser._parse_common_data(soup, {"all": False, "data_types": []}) == {}

class TestParse:
    def test_parse_default_returns_all_keys(self, parser, full_html):
        """TC-HP-56"""
        result = parser.parse(full_html)
        for key in ["metadata","headings","paragraphs","links","images","tables","lists","metrics","dom_tree"]:
            assert key in result
    def test_parse_with_schemas(self, parser, product_html):
        """TC-HP-57"""
        from schemas.schemas import product_schema
        result = parser.parse(product_html, {"products": product_schema})
        assert "products" in result and len(result["products"]) == 2
    def test_parse_empty_raises(self, parser):
        """TC-HP-58"""
        with pytest.raises(ValueError):
            parser.parse("")
    def test_parse_structured_only(self, parser, product_html):
        """TC-HP-59"""
        from schemas.schemas import product_schema
        result = parser.parse(product_html, {"products": product_schema},
                              {"all": False, "structured_only": True})
        assert "products" in result and "headings" not in result
    def test_parse_data_types_filter(self, parser, full_html):
        """TC-HP-60"""
        result = parser.parse(full_html, data_options={"all": False, "data_types": ["headings", "links"]})
        assert "headings" in result and "links" in result
        assert "images" not in result and "tables" not in result
