from bs4 import BeautifulSoup
from typing import Dict

class HTMLParser:

    """
    Парсер для HTML-документов.
    - извлекает метаданные
    - извлекает заголовки разного уровня
    - извлекает параграфы, ссылки, изображения
    - извлекает таблицы, списки
    - извлекает структурированные данные по заданным схемам
    - подсчитывает метрики документа
    - строит и визуализирует DOM-дерево документа
    """

    def __init__(self, parser_type: str = "html.parser"):
        self.parser_type = parser_type

    # Основной метод, выполняющий полный анализ документа
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
            "dom_tree": self.build_dom_tree(soup.find("html"))
        }
        if schemas:
            for schema_name, schema in schemas.items():
                data[schema_name] = self.extract_structured_blocks(soup, schema)

        return data
    
    # Проверяет корректность документа
    def validate_html(self, html: str):

        if not html or html.strip() == "":
            raise ValueError("HTML document is empty")
        
        html_lower = html.lower()
        if not ("<html" in html_lower 
                or "<body" in html_lower 
                or "<div" in html_lower):
            raise ValueError("Invalid HTML structure")

    # Извлекает метаданные из документа
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

    # Извлекает все заголовки (h1-h6) из документа и группирует их
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
    
    # Извлекает все параграфы из документа
    def extract_paragraphs(self, soup):
        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        return paragraphs
    
    # Извлекает все ссылки из документа
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
    
    # Извлекает все изображения из документа
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

    # Извлекает все таблицы из документа
    def extract_tables(self, soup):
        tables = []
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                row = []
                for cell in tr.find_all(["td", "th"]):
                    row.append(cell.get_text(strip=True))
                if row:
                    rows.append(row)
            if rows:
                tables.append({
                    "headers": rows[0] if rows else [],
                    "rows": rows[1:],
                    "row_count": len(rows) - 1 if rows else 0
                })
        return tables

    # Извлекает все списки из документа, разделяя ul и ol
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

    # Извлекает структурированные блоки данных по схеме
    # Схема определяет структуру блока
    def extract_structured_blocks(self, soup, schema):
        container = schema.get("container")
        if not container:
            return []

        tag, class_name = container
        if class_name:
            containers = soup.find_all(tag, class_=class_name)
        else:
            containers = soup.find_all(tag)

        results = []
        for container in containers:
            item = {}
            for field, field_info in schema.get("fields", {}).items():
                if isinstance(field_info, tuple) and len(field_info) == 2:
                    field_tag, field_class = field_info
                    if field_class:
                        element = container.find(field_tag, class_=field_class)
                    else:
                        element = container.find(field_tag)
                
                    if element:
                        raw_text = element.get_text()
                        cleaned_text = ' '.join(raw_text.split())
                        item[field] = cleaned_text
                    else:
                        item[field] = None
            
            if any(item.values()):
                results.append(item)

        return results

    # Подсчитывает различные метрики документа
    def get_document_metrics(self, soup):
        return {
            "links_count": len(soup.find_all("a")),
            "images_count": len(soup.find_all("img")),
            "paragraphs_count": len(soup.find_all("p")),
            "headings_count": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
            "tables_count": len(soup.find_all("table")),
            "lists_count": len(soup.find_all(["ul", "ol"])),
        }

    # Рекурсивно строит DOM-дерево документа
    def build_dom_tree(self, element):
        
        if not element:
            return None

        node = {
            "tag": element.name,
            "attributes": element.attrs if element.attrs else None,
            "children": []
        }

        for child in element.children:
            if hasattr(child, "name") and child.name:
                child_node = self.build_dom_tree(child)
                if child_node:
                    node["children"].append(child_node)
        
        return node

    # Рекурсивно визуализирует DOM-дерево документа в консоли
    def visualize_dom_tree(self, node, level=0):

        if node and "tag" in node:
            attrs = ""
            if node.get("attributes"):
                attrs = f" {node['attributes']}"
            
            print("--" * level + f"<{node['tag']}{attrs}>")

        for child in node.get("children", []):
            self.visualize_dom_tree(child, level + 1)