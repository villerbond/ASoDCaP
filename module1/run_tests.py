"""
Автономный тест-раннер для парсер-менеджера.
Запуск: python run_tests.py
"""

import sys
import os
import json as _json
import csv as _csv
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.html_parser import HTMLParser
from src.xml_parser import XMLParser
from src.parser_manager import ParserManager
from schemas.schemas import product_schema, article_schema
from bs4 import BeautifulSoup

# ─── helpers ────────────────────────────────────────────────────────────────

passed = []
failed = []

def assert_eq(a, b):
    assert a == b, f"Expected {b!r}, got {a!r}"

def assert_in(a, b):
    assert a in b, f"{a!r} not found in {b!r}"

def assert_(cond, msg="assertion failed"):
    assert cond, msg

def run(name, fn):
    try:
        fn()
        passed.append(name)
    except Exception as e:
        failed.append((name, str(e)))

def expect_raises(name, fn, exc=Exception):
    try:
        fn()
        failed.append((name, f"expected {exc.__name__}, no exception raised"))
    except exc:
        passed.append(name)
    except Exception as e:
        failed.append((name, f"wrong exception: {e}"))

# ─── fixtures ───────────────────────────────────────────────────────────────

FULL_HTML = """<!DOCTYPE html>
<html><head>
  <title>Test Page</title>
  <meta name="description" content="Test description">
  <meta name="keywords" content="test, parser">
</head><body>
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
</body></html>"""

PRODUCT_HTML = """<html><body>
  <div class="product">
    <h2>Widget</h2>
    <span class="price">9.99</span>
    <span class="rating">4.5</span>
  </div>
  <div class="product">
    <h2>Gadget</h2>
    <span class="price">19.99</span>
  </div>
</body></html>"""

ARTICLE_HTML = """<html><body>
  <article>
    <h2>Breaking News</h2>
    <span class="author">John Doe</span>
    <span class="date">2024-01-01</span>
  </article>
</body></html>"""

SAMPLE_XML = """<?xml version="1.0"?>
<catalog>
  <book id="1">
    <title>Python Basics</title>
    <author>Alice</author>
    <price>29.99</price>
  </book>
  <book id="2">
    <title>Advanced Python</title>
    <author>Bob</author>
  </book>
</catalog>"""

p    = HTMLParser()
xp   = XMLParser()
soup = BeautifulSoup(FULL_HTML, "html.parser")
ps   = BeautifulSoup(PRODUCT_HTML, "html.parser")
arts = BeautifulSoup(ARTICLE_HTML, "html.parser")
xs   = BeautifulSoup(SAMPLE_XML, "xml")

# ============================================================================
print("=" * 60)
print("БЛОК 1: HTMLParser — validate_html")
print("=" * 60)

run("TC-HP-01 valid HTML passes",
    lambda: p.validate_html(FULL_HTML))
expect_raises("TC-HP-02 empty string raises",
    lambda: p.validate_html(""), ValueError)
expect_raises("TC-HP-03 whitespace raises",
    lambda: p.validate_html("   \n\t"), ValueError)
expect_raises("TC-HP-04 plain text raises",
    lambda: p.validate_html("just plain text"), ValueError)
run("TC-HP-05 minimal div passes",
    lambda: p.validate_html("<div>ok</div>"))

# ============================================================================
print("\nБЛОК 2: HTMLParser — extract_metadata")
print("=" * 60)

meta = p.extract_metadata(soup)
run("TC-HP-06 title extracted",
    lambda: assert_eq(meta["title"], "Test Page"))
run("TC-HP-07 description extracted",
    lambda: assert_eq(meta["description"], "Test description"))
run("TC-HP-08 keywords extracted",
    lambda: assert_eq(meta["keywords"], "test, parser"))
run("TC-HP-09 no title -> None", lambda: assert_eq(
    p.extract_metadata(BeautifulSoup("<html><body></body></html>", "html.parser"))["title"], None))
run("TC-HP-10 no meta -> None desc", lambda: assert_eq(
    p.extract_metadata(BeautifulSoup("<html><head><title>X</title></head></html>", "html.parser"))["description"], None))

# ============================================================================
print("\nБЛОК 3: HTMLParser — extract_headings")
print("=" * 60)

h = p.extract_headings(soup)
run("TC-HP-11 h1 extracted",
    lambda: assert_in("Main Heading", h["h1"]))
run("TC-HP-12 h2 extracted",
    lambda: assert_in("Sub Heading", h["h2"]))
run("TC-HP-13 all levels h1-h6",
    lambda: [assert_in(f"h{i}", h) for i in range(1, 7)])
run("TC-HP-14 missing level -> empty list",
    lambda: assert_eq(h["h4"], []))
run("TC-HP-15 empty heading excluded", lambda: assert_eq(
    p.extract_headings(BeautifulSoup("<html><body><h1>  </h1><h1>Real</h1></body></html>", "html.parser"))["h1"],
    ["Real"]))

# ============================================================================
print("\nБЛОК 4: HTMLParser — extract_paragraphs")
print("=" * 60)

paras = p.extract_paragraphs(soup)
run("TC-HP-16 paragraphs count",
    lambda: assert_eq(len(paras), 2))
run("TC-HP-17 paragraph text",
    lambda: assert_in("First paragraph.", paras))
run("TC-HP-18 empty paragraph excluded", lambda: assert_eq(
    p.extract_paragraphs(BeautifulSoup("<html><body><p></p><p>Text</p></body></html>", "html.parser")),
    ["Text"]))

# ============================================================================
print("\nБЛОК 5: HTMLParser — extract_links")
print("=" * 60)

links = p.extract_links(soup)
run("TC-HP-19 links count",
    lambda: assert_eq(len(links), 2))
run("TC-HP-20 link url",
    lambda: assert_in("https://example.com", [l["url"] for l in links]))
run("TC-HP-21 link text",
    lambda: assert_in("Example", [l["text"] for l in links]))
run("TC-HP-22 no href excluded", lambda: assert_eq(
    p.extract_links(BeautifulSoup("<html><body><a>No href</a></body></html>", "html.parser")), []))

# ============================================================================
print("\nБЛОК 6: HTMLParser — extract_images")
print("=" * 60)

imgs = p.extract_images(soup)
no_alt_img = next(i for i in imgs if i["src"] == "no-alt.png")
run("TC-HP-23 images count",
    lambda: assert_eq(len(imgs), 2))
run("TC-HP-24 image src",
    lambda: assert_in("image.jpg", [i["src"] for i in imgs]))
run("TC-HP-25 no alt -> empty string",
    lambda: assert_eq(no_alt_img["alt"], ""))
run("TC-HP-26 no src excluded", lambda: assert_eq(
    p.extract_images(BeautifulSoup("<html><body><img alt='x'></body></html>", "html.parser")), []))

# ============================================================================
print("\nБЛОК 7: HTMLParser — extract_tables")
print("=" * 60)

tables = p.extract_tables(soup)
run("TC-HP-27 table count",
    lambda: assert_eq(len(tables), 1))
run("TC-HP-28 table headers",
    lambda: assert_eq(tables[0]["headers"], ["Name", "Price"]))
run("TC-HP-29 table rows contain Apple",
    lambda: assert_in(["Apple", "1.00"], tables[0]["rows"]))
run("TC-HP-30 row_count correct",
    lambda: assert_eq(tables[0]["row_count"], 2))

# ============================================================================
print("\nБЛОК 8: HTMLParser — extract_lists")
print("=" * 60)

lsts = p.extract_lists(soup)
run("TC-HP-31 unordered list",
    lambda: assert_in(["Item A", "Item B"], lsts["unordered"]))
run("TC-HP-32 ordered list",
    lambda: assert_in(["Step 1", "Step 2"], lsts["ordered"]))
run("TC-HP-33 empty ul excluded", lambda: assert_eq(
    p.extract_lists(BeautifulSoup("<html><body><ul></ul></body></html>", "html.parser"))["unordered"], []))
run("TC-HP-34 both keys always present",
    lambda: (assert_in("unordered", lsts), assert_in("ordered", lsts)))

# ============================================================================
print("\nБЛОК 9: HTMLParser — extract_structured_blocks")
print("=" * 60)

prods = p.extract_structured_blocks(ps, product_schema)
gadget = next(r for r in prods if r["name"] == "Gadget")
art_res = p.extract_structured_blocks(arts, article_schema)

run("TC-HP-35 products count",
    lambda: assert_eq(len(prods), 2))
run("TC-HP-36 product name",
    lambda: assert_in("Widget", [r["name"] for r in prods]))
run("TC-HP-37 missing field -> None",
    lambda: assert_eq(gadget["rating"], None))
run("TC-HP-38 article schema",
    lambda: (assert_eq(art_res[0]["title"], "Breaking News"),
             assert_eq(art_res[0]["author"], "John Doe")))
run("TC-HP-39 no container -> empty",
    lambda: assert_eq(p.extract_structured_blocks(soup, {}), []))

# ============================================================================
print("\nБЛОК 10: HTMLParser — get_document_metrics")
print("=" * 60)

m = p.get_document_metrics(soup)
run("TC-HP-40 links_count",      lambda: assert_eq(m["links_count"], 2))
run("TC-HP-41 images_count",     lambda: assert_eq(m["images_count"], 2))
run("TC-HP-42 paragraphs_count", lambda: assert_eq(m["paragraphs_count"], 2))
run("TC-HP-43 headings_count",   lambda: assert_eq(m["headings_count"], 3))
run("TC-HP-44 tables_count",     lambda: assert_eq(m["tables_count"], 1))
run("TC-HP-45 lists_count",      lambda: assert_eq(m["lists_count"], 2))

# ============================================================================
print("\nБЛОК 11: HTMLParser — build_dom_tree / visualize_dom_tree")
print("=" * 60)

tree = p.build_dom_tree(soup.find("html"))
run("TC-HP-46 root tag = html",
    lambda: assert_eq(tree["tag"], "html"))
run("TC-HP-47 children present",
    lambda: assert_(len(tree["children"]) > 0))
run("TC-HP-48 None input -> None",
    lambda: assert_eq(p.build_dom_tree(None), None))
run("TC-HP-49 attributes captured", lambda: assert_(
    p.build_dom_tree(
        BeautifulSoup('<html><body><a href="x">l</a></body></html>', "html.parser").find("html")
    )["children"][0]["children"][0]["attributes"] == {"href": "x"}))

import io
from contextlib import redirect_stdout
buf = io.StringIO()
with redirect_stdout(buf):
    p.visualize_dom_tree(tree)
run("TC-HP-50 visualize_dom_tree no error",
    lambda: assert_("<html>" in buf.getvalue()))

# ============================================================================
print("\nБЛОК 12: HTMLParser — parse (интеграционный)")
print("=" * 60)

result  = p.parse(FULL_HTML)
result2 = p.parse(PRODUCT_HTML, {"products": product_schema})

run("TC-HP-51 parse returns all keys",
    lambda: [assert_in(k, result) for k in
             ["metadata","headings","paragraphs","links","images","tables","lists","metrics","dom_tree"]])
run("TC-HP-52 parse with schemas adds key",
    lambda: (assert_in("products", result2), assert_eq(len(result2["products"]), 2)))
expect_raises("TC-HP-53 parse empty -> ValueError",
    lambda: p.parse(""), ValueError)

# ============================================================================
print("\nБЛОК 13: XMLParser")
print("=" * 60)

xp2 = XMLParser()
xr  = xp2.parse(SAMPLE_XML)
els = xp2.extract_elements(xs)
tags  = [e["tag"]  for e in els]
texts = [e["text"] for e in els]

run("TC-XP-01 parser_type = xml",        lambda: assert_eq(xp2.parser_type, "xml"))
run("TC-XP-02 root = catalog",           lambda: assert_eq(xr["root"], "catalog"))
run("TC-XP-03 elements key present",     lambda: assert_in("elements", xr))
run("TC-XP-04 elements is list",         lambda: assert_(isinstance(xr["elements"], list)))
run("TC-XP-05 elements not empty",       lambda: assert_(len(xr["elements"]) > 0))
run("TC-XP-06 single root tag",          lambda: assert_eq(xp2.parse("<root><child>T</child></root>")["root"], "root"))
run("TC-XP-07 each elem has 'tag'",      lambda: [assert_in("tag",  e) for e in els])
run("TC-XP-08 each elem has 'text'",     lambda: [assert_in("text", e) for e in els])
run("TC-XP-09 title tag present",        lambda: assert_in("title", tags))
run("TC-XP-10 text extracted",           lambda: assert_in("Python Basics", texts))
run("TC-XP-11 nested tags all included", lambda: assert_({"book","title","author","price"}.issubset(set(tags))))

# ============================================================================
print("\nБЛОК 14: ParserManager — init / get_parser")
print("=" * 60)

pm = ParserManager()
run("TC-PM-01 has html_parser",        lambda: assert_(isinstance(pm.html_parser, HTMLParser)))
run("TC-PM-02 has xml_parser",         lambda: assert_(isinstance(pm.xml_parser, XMLParser)))
run("TC-PM-03 products schema",        lambda: assert_in("products", pm.schemas))
run("TC-PM-04 articles schema",        lambda: assert_in("articles", pm.schemas))
run("TC-PM-05 initial stats = 0",
    lambda: (assert_eq(pm.get_statistics()["files_processed"], 0),
             assert_eq(pm.get_statistics()["files_failed"], 0)))
run("TC-PM-06 .html -> HTMLParser",    lambda: assert_(isinstance(pm.get_parser("page.html"), HTMLParser)))
run("TC-PM-07 .xml  -> XMLParser",     lambda: assert_(isinstance(pm.get_parser("data.xml"),  XMLParser)))
expect_raises("TC-PM-08 .pdf -> ValueError",
    lambda: pm.get_parser("file.pdf"), ValueError)
expect_raises("TC-PM-09 no ext -> ValueError",
    lambda: pm.get_parser("noextension"), ValueError)

# ============================================================================
print("\nБЛОК 15: ParserManager — process_file")
print("=" * 60)

with tempfile.TemporaryDirectory() as tmp:
    hf = os.path.join(tmp, "test.html")
    xf = os.path.join(tmp, "test.xml")
    with open(hf, "w", encoding="utf-8") as f: f.write(FULL_HTML)
    with open(xf, "w", encoding="utf-8") as f: f.write(SAMPLE_XML)

    pm2 = ParserManager()
    hr = pm2.process_file(hf)
    xr2 = pm2.process_file(xf)
    none_r = pm2.process_file("nonexistent.html")

    run("TC-PM-10 html -> dict",        lambda: assert_(isinstance(hr, dict)))
    run("TC-PM-11 html has metadata",   lambda: assert_in("metadata", hr))
    run("TC-PM-12 xml -> dict",         lambda: assert_(isinstance(xr2, dict)))
    run("TC-PM-13 xml has root",        lambda: assert_in("root", xr2))
    run("TC-PM-14 missing file -> None",lambda: assert_eq(none_r, None))
    run("TC-PM-15 stats increment",
        lambda: assert_eq(pm2.get_statistics()["files_processed"], 2))
    run("TC-PM-16 failed increments",
        lambda: assert_eq(pm2.get_statistics()["files_failed"], 1))

    pm3 = ParserManager()
    sr1 = pm3.process_file(hf, selected_schemas=["products"])
    sr2 = pm3.process_file(hf, selected_schemas=["all"])
    run("TC-PM-17 selected_schemas filter",
        lambda: (assert_in("products", sr1), assert_("articles" not in sr1)))
    run("TC-PM-18 selected_schemas all",
        lambda: (assert_in("products", sr2), assert_in("articles", sr2)))

# ============================================================================
print("\nБЛОК 16: ParserManager — process_directory")
print("=" * 60)

with tempfile.TemporaryDirectory() as tmp:
    mixed = os.path.join(tmp, "mixed")
    os.makedirs(mixed)
    with open(os.path.join(mixed, "a.html"), "w") as f: f.write(FULL_HTML)
    with open(os.path.join(mixed, "b.xml"),  "w") as f: f.write(SAMPLE_XML)
    with open(os.path.join(mixed, "c.txt"),  "w") as f: f.write("ignored")

    empty_dir = os.path.join(tmp, "empty")
    os.makedirs(empty_dir)

    pm4 = ParserManager()
    dr = pm4.process_directory(mixed)
    run("TC-PM-19 returns list",                  lambda: assert_(isinstance(dr, list)))
    run("TC-PM-20 html+xml processed txt ignored",lambda: assert_eq(len(dr), 2))
    run("TC-PM-21 stats reset per run",
        lambda: assert_eq(pm4.get_statistics()["files_processed"], 2))
    expect_raises("TC-PM-22 invalid dir -> ValueError",
        lambda: pm4.process_directory("/path/not/exist"), ValueError)
    run("TC-PM-23 empty dir -> empty list",
        lambda: assert_eq(pm4.process_directory(empty_dir), []))

# ============================================================================
print("\nБЛОК 17: ParserManager — save_json")
print("=" * 60)

with tempfile.TemporaryDirectory() as tmp:
    pm5 = ParserManager()

    jout = os.path.join(tmp, "out", "result.json")
    pm5.save_json({"key": "value"}, jout)
    with open(jout, encoding="utf-8") as f:
        loaded = _json.load(f)
    run("TC-PM-24 file created",     lambda: assert_(os.path.exists(jout)))
    run("TC-PM-25 content correct",  lambda: assert_eq(loaded, {"key": "value"}))

    uout = os.path.join(tmp, "unicode.json")
    pm5.save_json({"name": "Привет"}, uout)
    with open(uout, encoding="utf-8") as f:
        uc = f.read()
    run("TC-PM-26 unicode preserved",lambda: assert_("Привет" in uc))

    nested = os.path.join(tmp, "a", "b", "c.json")
    pm5.save_json({}, nested)
    run("TC-PM-27 nested dirs created", lambda: assert_(os.path.exists(nested)))

# ============================================================================
print("\nБЛОК 18: ParserManager — save_csv")
print("=" * 60)

with tempfile.TemporaryDirectory() as tmp:
    pm6 = ParserManager()

    cout = os.path.join(tmp, "result.csv")
    pm6.save_csv([{"name": "Widget", "price": "9.99"}], cout)
    with open(cout, encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))
    run("TC-PM-28 csv file created",     lambda: assert_(os.path.exists(cout)))
    run("TC-PM-29 headers correct",
        lambda: assert_eq(set(rows[0].keys()), {"name", "price"}))
    run("TC-PM-30 single row written",   lambda: assert_eq(len(rows), 1))

    cout2 = os.path.join(tmp, "multi.csv")
    pm6.save_csv([{"n": "A"}, {"n": "B"}], cout2)
    with open(cout2, encoding="utf-8") as f:
        rows2 = list(_csv.DictReader(f))
    run("TC-PM-31 multiple rows written",lambda: assert_eq(len(rows2), 2))

    import io
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        pm6.save_csv([], os.path.join(tmp, "empty.csv"))
    run("TC-PM-32 empty data -> warning",
        lambda: assert_("No data" in buf2.getvalue()))

# ============================================================================
print("\nБЛОК 19: ParserManager — get_statistics")
print("=" * 60)

with tempfile.TemporaryDirectory() as tmp:
    hf = os.path.join(tmp, "test.html")
    xf = os.path.join(tmp, "test.xml")
    with open(hf, "w") as f: f.write(FULL_HTML)
    with open(xf, "w") as f: f.write(SAMPLE_XML)

    pm7 = ParserManager()
    s7 = pm7.get_statistics()
    s7["files_processed"] = 999
    run("TC-PM-33 returns copy",
        lambda: assert_eq(pm7.get_statistics()["files_processed"], 0))

    pm8 = ParserManager()
    pm8.process_file(hf)
    pm8.process_file(xf)
    run("TC-PM-34 accumulates across files",
        lambda: assert_eq(pm8.get_statistics()["files_processed"], 2))

# ============================================================================
print("\n" + "=" * 60)
print(f"  ИТОГО: PASSED {len(passed)}  |  FAILED {len(failed)}")
print("=" * 60)

if failed:
    print("\nПроваленные тесты:")
    for name, err in failed:
        print(f"  FAIL  {name}")
        print(f"        {err}")

print()
for name in passed:
    print(f"  PASS  {name}")

sys.exit(1 if failed else 0)
