"""
Тест-кейсы для ParserManager
"""
import pytest
import os
import json
import csv
import tempfile
from src.parser_manager import ParserManager
from src.html_parser import HTMLParser
from src.xml_parser import XMLParser
from schemas.schemas import product_schema, article_schema, get_schemas

SAMPLE_HTML = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body>
  <h1>Hello</h1><p>Paragraph.</p>
  <a href="https://example.com">Link</a>
  <div class="product"><h2>Widget</h2><span class="price">9.99</span></div>
  <article><h2>News</h2><span class="author">Bob</span><span class="date">2024</span></article>
</body></html>"""

SAMPLE_XML = """<?xml version="1.0"?><catalog><book><title>Python</title></book></catalog>"""

@pytest.fixture
def manager():
    return ParserManager()

@pytest.fixture
def manager_with_schemas():
    return ParserManager(schemas=get_schemas())

@pytest.fixture
def html_file(tmp_path):
    f = tmp_path / "test.html"
    f.write_text(SAMPLE_HTML, encoding="utf-8")
    return str(f)

@pytest.fixture
def xml_file(tmp_path):
    f = tmp_path / "test.xml"
    f.write_text(SAMPLE_XML, encoding="utf-8")
    return str(f)

@pytest.fixture
def mixed_dir(tmp_path):
    (tmp_path / "a.html").write_text(SAMPLE_HTML, encoding="utf-8")
    (tmp_path / "b.xml").write_text(SAMPLE_XML, encoding="utf-8")
    (tmp_path / "c.txt").write_text("ignored", encoding="utf-8")
    return str(tmp_path)

class TestParserManagerInit:
    def test_has_html_parser(self, manager):
        """TC-PM-01"""
        assert isinstance(manager.html_parser, HTMLParser)
    def test_has_xml_parser(self, manager):
        """TC-PM-02"""
        assert isinstance(manager.xml_parser, XMLParser)
    def test_schemas_empty_by_default(self, manager):
        """TC-PM-03"""
        assert manager.schemas == {}
    def test_schemas_set_via_constructor(self):
        """TC-PM-04"""
        pm = ParserManager(schemas={"products": product_schema, "articles": article_schema})
        assert "products" in pm.schemas and "articles" in pm.schemas
    def test_schemas_set_via_set_schemas(self, manager):
        """TC-PM-04b"""
        manager.set_schemas({"products": product_schema})
        assert "products" in manager.schemas
    def test_initial_stats(self, manager):
        """TC-PM-05"""
        stats = manager.get_statistics()
        assert stats["files_processed"] == 0 and stats["files_failed"] == 0

class TestGetParser:
    def test_html_extension_returns_html_parser(self, manager):
        """TC-PM-06"""
        assert isinstance(manager.get_parser("page.html"), HTMLParser)
    def test_xml_extension_returns_xml_parser(self, manager):
        """TC-PM-07"""
        assert isinstance(manager.get_parser("data.xml"), XMLParser)
    def test_unsupported_extension_raises(self, manager):
        """TC-PM-08"""
        with pytest.raises(ValueError, match="Unsupported file format"):
            manager.get_parser("file.pdf")
    def test_no_extension_raises(self, manager):
        """TC-PM-09"""
        with pytest.raises(ValueError):
            manager.get_parser("noextension")

class TestProcessFile:
    def test_process_html_file_returns_dict(self, manager, html_file):
        """TC-PM-10"""
        assert isinstance(manager.process_file(html_file), dict)
    def test_process_html_file_has_metadata(self, manager, html_file):
        """TC-PM-11"""
        assert "metadata" in manager.process_file(html_file)
    def test_process_xml_file_returns_dict(self, manager, xml_file):
        """TC-PM-12"""
        assert isinstance(manager.process_file(xml_file), dict)
    def test_process_xml_has_root(self, manager, xml_file):
        """TC-PM-13"""
        assert "root" in manager.process_file(xml_file)
    def test_nonexistent_file_returns_none(self, manager):
        """TC-PM-14"""
        result = manager.process_file("nonexistent.html")
        assert result is None
        assert manager.get_statistics()["files_failed"] == 1
    def test_stats_increment_on_success(self, manager, html_file):
        """TC-PM-15"""
        manager.process_file(html_file)
        assert manager.get_statistics()["files_processed"] == 1
    def test_selected_schemas_as_dict(self, html_file):
        """TC-PM-16"""
        pm = ParserManager()
        result = pm.process_file(html_file, selected_schemas={"products": product_schema})
        assert "products" in result
        assert "articles" not in result
    def test_schemas_from_constructor_applied(self, html_file):
        """TC-PM-17"""
        pm = ParserManager(schemas={"products": product_schema, "articles": article_schema})
        result = pm.process_file(html_file)
        assert "products" in result and "articles" in result
    def test_data_options_headings_only(self, manager, html_file):
        result = manager.process_file(
            html_file,
            data_options={"all": False, "data_types": ["headings"]}
        )
        assert "headings" in result
        assert "links" not in result

class TestProcessDirectory:
    def test_returns_list(self, manager, mixed_dir):
        """TC-PM-19"""
        assert isinstance(manager.process_directory(mixed_dir), list)
    def test_processes_html_and_xml(self, manager, mixed_dir):
        """TC-PM-20"""
        assert len(manager.process_directory(mixed_dir)) == 2
    def test_stats_reset_before_run(self, manager, mixed_dir):
        """TC-PM-21"""
        manager.process_file("nonexistent.html")
        manager.process_directory(mixed_dir)
        stats = manager.get_statistics()
        assert stats["files_processed"] == 2 and stats["files_failed"] == 0
    def test_invalid_directory_raises(self, manager):
        """TC-PM-22"""
        with pytest.raises(ValueError):
            manager.process_directory("/path/that/does/not/exist")
    def test_empty_directory_returns_empty_list(self, manager, tmp_path):
        """TC-PM-23"""
        assert manager.process_directory(str(tmp_path)) == []

class TestSaveJson:
    def test_file_created(self, manager, tmp_path):
        """TC-PM-24"""
        out = str(tmp_path / "out" / "result.json")
        manager.save_json({"key": "value"}, out)
        assert os.path.exists(out)
    def test_content_correct(self, manager, tmp_path):
        """TC-PM-25"""
        out = str(tmp_path / "result.json")
        manager.save_json({"hello": "world"}, out)
        with open(out, encoding="utf-8") as f:
            assert json.load(f) == {"hello": "world"}
    def test_unicode_preserved(self, manager, tmp_path):
        """TC-PM-26"""
        out = str(tmp_path / "unicode.json")
        manager.save_json({"name": "Привет"}, out)
        assert "Привет" in open(out, encoding="utf-8").read()
    def test_nested_dirs_created(self, manager, tmp_path):
        """TC-PM-27"""
        out = str(tmp_path / "a" / "b" / "c.json")
        manager.save_json({}, out)
        assert os.path.exists(out)

class TestSaveCsv:
    def test_file_created(self, manager, tmp_path):
        """TC-PM-28"""
        out = str(tmp_path / "result.csv")
        manager.save_csv([{"a": 1, "b": 2}], out)
        assert os.path.exists(out)
    def test_headers_written(self, manager, tmp_path):
        """TC-PM-29"""
        out = str(tmp_path / "result.csv")
        manager.save_csv([{"name": "X", "price": "9.99"}], out)
        with open(out, encoding="utf-8") as f:
            assert set(csv.DictReader(f).fieldnames) == {"name", "price"}
    def test_rows_written(self, manager, tmp_path):
        """TC-PM-30"""
        out = str(tmp_path / "result.csv")
        manager.save_csv([{"name": "Widget"}, {"name": "Gadget"}], out)
        with open(out, encoding="utf-8") as f:
            assert len(list(csv.DictReader(f))) == 2
    def test_empty_data_no_file_content(self, manager, tmp_path, capsys):
        """TC-PM-31"""
        out = str(tmp_path / "empty.csv")
        manager.save_csv([], out)
        assert "No data" in capsys.readouterr().out
        assert not os.path.exists(out)

class TestGetStatistics:
    def test_returns_copy(self, manager):
        """TC-PM-32"""
        stats = manager.get_statistics()
        stats["files_processed"] = 999
        assert manager.get_statistics()["files_processed"] == 0
    def test_accumulates_across_files(self, manager, html_file, xml_file):
        """TC-PM-33"""
        manager.process_file(html_file)
        manager.process_file(xml_file)
        assert manager.get_statistics()["files_processed"] == 2
