"""
Тест-кейсы для main.py
"""

import os
import sys
import json
import csv
import pytest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

SAMPLE_HTML = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body>
  <h1>Hello</h1>
  <p>Paragraph.</p>
  <a href="https://example.com">Link</a>
  <div class="product"><h2>Widget</h2><span class="price">9.99</span><span class="rating">4.5</span></div>
  <article><h2>News</h2><span class="author">Bob</span><span class="date">2024</span></article>
</body></html>"""

SAMPLE_XML = """<?xml version="1.0"?><catalog><book><title>Python</title></book></catalog>"""


@pytest.fixture
def html_file(tmp_path):
    f = tmp_path / "sample.html"
    f.write_text(SAMPLE_HTML, encoding="utf-8")
    return str(f)

@pytest.fixture
def xml_file(tmp_path):
    f = tmp_path / "sample.xml"
    f.write_text(SAMPLE_XML, encoding="utf-8")
    return str(f)

@pytest.fixture
def out_dir(tmp_path):
    d = tmp_path / "output"
    return str(d)

@pytest.fixture
def mixed_dir(tmp_path):
    (tmp_path / "a.html").write_text(SAMPLE_HTML, encoding="utf-8")
    (tmp_path / "b.xml").write_text(SAMPLE_XML, encoding="utf-8")
    return str(tmp_path)


# ===========================================================================
# TC-MA-01..04  Сохранение в JSON
# ===========================================================================

class TestSaveJson:

    def test_json_file_created(self, html_file, out_dir):
        """TC-MA-01"""
        sys.argv = ["main.py", html_file, "--format", "json", "--output-dir", out_dir]
        main()
        assert any(f.endswith(".json") for f in os.listdir(out_dir))

    def test_json_filename_matches_source(self, html_file, out_dir):
        """TC-MA-02"""
        sys.argv = ["main.py", html_file, "--format", "json", "--output-dir", out_dir]
        main()
        assert "sample.json" in os.listdir(out_dir)

    def test_json_content_valid(self, html_file, out_dir):
        """TC-MA-03"""
        sys.argv = ["main.py", html_file, "--format", "json", "--output-dir", out_dir]
        main()
        json_file = os.path.join(out_dir, "sample.json")
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_json_has_headings(self, html_file, out_dir):
        """TC-MA-04"""
        sys.argv = ["main.py", html_file, "--format", "json", "--output-dir", out_dir]
        main()
        json_file = os.path.join(out_dir, "sample.json")
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        assert "headings" in data


# ===========================================================================
# TC-MA-05..07  Сохранение в CSV
# ===========================================================================

class TestSaveCsv:

    def test_csv_file_created_for_products(self, html_file, out_dir):
        """TC-MA-05"""
        sys.argv = ["main.py", html_file, "--format", "csv",
                    "--output-dir", out_dir, "--schemas", "products"]
        main()
        files = os.listdir(out_dir)
        assert any("products" in f and f.endswith(".csv") for f in files)

    def test_csv_products_content(self, html_file, out_dir):
        """TC-MA-06"""
        sys.argv = ["main.py", html_file, "--format", "csv",
                    "--output-dir", out_dir, "--schemas", "products"]
        main()
        csv_file = next(
            os.path.join(out_dir, f) for f in os.listdir(out_dir)
            if "products" in f and f.endswith(".csv")
        )
        with open(csv_file, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 0

    def test_no_format_no_output_files(self, html_file, out_dir):
        """TC-MA-07"""
        sys.argv = ["main.py", html_file, "--output-dir", out_dir]
        main()
        if os.path.exists(out_dir):
            assert len(os.listdir(out_dir)) == 0


# ===========================================================================
# TC-MA-08..11  data_options флаги
# ===========================================================================

class TestDataOptions:

    def test_structured_only_no_headings(self, html_file, out_dir):
        """TC-MA-08"""
        sys.argv = ["main.py", html_file, "--format", "json",
                    "--structured-only", "--output-dir", out_dir]
        main()
        with open(os.path.join(out_dir, "sample.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert "headings" not in data

    def test_structured_only_has_products(self, html_file, out_dir):
        """TC-MA-09"""
        sys.argv = ["main.py", html_file, "--format", "json",
                    "--structured-only", "--output-dir", out_dir,
                    "--schemas", "products"]
        main()
        with open(os.path.join(out_dir, "sample.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert "products" in data

    def test_data_types_headings_only(self, html_file, out_dir):
        """TC-MA-10"""
        sys.argv = ["main.py", html_file, "--format", "json",
                    "--data-types", "headings", "--output-dir", out_dir]
        main()
        with open(os.path.join(out_dir, "sample.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert "headings" in data
        assert "links" not in data

    def test_all_data_has_all_sections(self, html_file, out_dir):
        """TC-MA-11"""
        sys.argv = ["main.py", html_file, "--format", "json",
                    "--all-data", "--output-dir", out_dir]
        main()
        with open(os.path.join(out_dir, "sample.json"), encoding="utf-8") as f:
            data = json.load(f)
        for key in ["metadata", "headings", "links", "images", "metrics"]:
            assert key in data


# ===========================================================================
# TC-MA-12..14  Обработка директории и XML
# ===========================================================================

class TestDirectoryAndXml:

    def test_xml_file_json(self, xml_file, out_dir):
        """TC-MA-12"""
        sys.argv = ["main.py", xml_file, "--format", "json", "--output-dir", out_dir]
        main()
        assert any(f.endswith(".json") for f in os.listdir(out_dir))

    def test_directory_creates_multiple_files(self, mixed_dir, out_dir):
        """TC-MA-13"""
        sys.argv = ["main.py", mixed_dir, "--format", "json", "--output-dir", out_dir]
        main()
        json_files = [f for f in os.listdir(out_dir) if f.endswith(".json")]
        assert len(json_files) >= 2

    def test_output_dir_created_automatically(self, html_file, tmp_path):
        """TC-MA-14"""
        out = str(tmp_path / "new" / "nested" / "output")
        sys.argv = ["main.py", html_file, "--format", "json", "--output-dir", out]
        main()
        assert os.path.exists(out)


# ===========================================================================
# TC-MA-15  Схемы
# ===========================================================================

class TestSchemas:

    def test_schemas_filter_products_only(self, html_file, out_dir):
        """TC-MA-15"""
        sys.argv = ["main.py", html_file, "--format", "json",
                    "--schemas", "products", "--output-dir", out_dir]
        main()
        with open(os.path.join(out_dir, "sample.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert "products" in data
        assert "articles" not in data
