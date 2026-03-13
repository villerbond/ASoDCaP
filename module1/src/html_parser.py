from bs4 import BeautifulSoup
from typing import Dict

class HTMLParser:
    def __init__(self, parser_type: str = "html.parser"):
        self.parser_type = parser_type

    def parse(self, html: str, schemas: Dict = None):
        self.validate_html(html)
        soup = BeautifulSoup(html, self.parser_type)
        data = {
            "metadata": self.extract_metadata(soup),
            "headings": self.extract_headings(soup),
            "paragraphs": self.extract_paragraphs(soup),
            "links": self.extract_links(soup),
            "images": self.extract_images(soup),
            "tables": self.extract_tables(soup),
            "lists": self.extract_lists(soup),
            "metrics": self.get_document_metrics(soup),
            "dom_tree": self.build_dom_tree(soup.find(html))
        }
        if schemas:
            for schema_name, schema in schemas.items():
                data[schema_name] = self.extract_structured_blocks(soup, schema)

        return data
    
    def validate_html(self, html: str):

        if not html or html.strip() == "":
            raise ValueError("HTML document is empty")
        
        html_lower = html.lower()
        if not ("<html" in html_lower 
                or "<body" in html_lower 
                or "<div" in html_lower):
            raise ValueError("Invalid HTML structure")

    def extract_metadata(self, soup):
        metadata = {
            "title": soup.title.string if soup.title else None,
            "description": None,
            "keywords": None
        }

        meta_descriptions = soup.find("meta", attrs={"name": "description"})
        if meta_descriptions:
            metadata["description"] = meta_descriptions.get("content")
        
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords:
            metadata["keywords"] = meta_keywords.get("content")

        return metadata

    def extract_headings(self, soup):

        headings = {}

        for heading_level in range(1, 7):
            tag = f"h{heading_level}"
            elements = []
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text:
                    elements.append(text)
            headings[tag] = elements
        return headings
    
    def extract_paragraphs(self, soup):
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        return paragraphs
    
    def extract_links(self, soup):
        links = []
        for a in soup.find_all("a"):
            href = a.get("href")
            text = a.get_text(strip=True)
            if href:
                links.append({
                    "url": href,
                    "text": text
                })
        return links
    
    def extract_images(self, soup):
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                images.append({
                    "src": src,
                    "alt": alt,
                })
        return images

    def extract_tables(self, soup):
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                row = []
                for cell in tr.find_all(["td", "th"]):
                    row.append(cell.get_text(strip=True))
                if row:
                    rows.appens(row)
            if rows:
                tables.appens({
                    "headers": rows[0] if rows else [],
                    "rows": rows[1:],
                    "row_count": len(rows) - 1 if rows else 0
                })
        return tables

    def extract_lists(self, soup):
        lists = {
            "unordered": [],
            "ordered": []
        }

        for ul in soup.find_all("ul"):
            items = []
            for li in ul.find_all("li"):
                items.append(li.get_text(strip=True))
            if items:
                lists["unordered"].append(items)

        for ol in soup.find_all("ol"):
            items = []
            for li in ol.find_all("li"):
                items.append(li.get_text(strip=True))
            if items:
                lists["ordered"].append(items)

        return lists

    def extract_structured_blocks(self, soup, schema):
        tag, class_name = schema["container"]
        containers = soup.find_all(tag, class_=class_name)
        results = []
        for container in containers:
            item = {}
            for field, (field_tag, field_class) in schema["fields"].items():
                if (field_class):
                    element = container.find(field_tag, class_=field_class)
                else:
                    element = container.find(field_tag)
                
                if (element):
                    item[field] = element.get_text(strip=True)
                else:
                    item[field] = None
                
            results.append(item)
        return results

    def get_document_metrics(self, soup):
        return {
            "links": len(soup.find_all("a")),
            "images": len(soup.find_all("img")),
            "paragraphs": len(soup.find_all("p")),
            "headings": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
        }

    def build_dom_tree(self, element):
        
        node = {
            "tag": element.name,
            "children": []
        }

        for child in element.children:
            if hasattr(child, "name") and child.name:
                node["children"].append(
                    self.build_dom_tree(child)
                )
        
        return node

    def visualize_dom_tree(self, node, level=0):
        print("--" * level + node["tag"])
        for child in node["children"]:
            self.visualize_dom_tree(child, level + 1)