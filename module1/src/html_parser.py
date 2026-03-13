from bs4 import BeautifulSoup

class HTMLParser:
    def __init__(self, parser_type: str = "html.parser"):
        self.parser_type = parser_type

    def parse(self, html: str, schemas: list = None):
        self.validate_html(html)
        soup = BeautifulSoup(html, self.parser_type)
        data = {
            "headings": self.extract_headings(soup),
            "paragraphs": self.extract_paragraphs(soup),
            "links": self.extract_links(soup),
            "images": self.extract_images(soup),
            "metrics": self.get_document_metrics(soup),
            "dom_tree": self.build_dom_tree(soup.html)
        }
        if schemas:
            for schema_name, schema in schemas:
                data[schema_name] = self.extract_structured_blocks(soup, schema)

        return data
    
    def validate_html(self, html: str):
        if not html or html.strip() == "":
            raise ValueError("HTML document is empty")
        if "<html" not in html.lower():
            raise ValueError("Invalid HTML structure")

    def extract_headings(self, soup):

        headings = {
            "h1": [],
            "h2": [],
            "h3": [],
            "h4": [],
            "h5": [],
            "h6": []
        }

        for tag in headings.keys():
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if text:
                    headings[tag].append(text)

        return headings
    
    def extract_paragraphs(self, soup):
        paragraphs = []
        for tag in soup.find_all("p"):
            text = tag.get_text(strip=True)
            if text:
                paragraphs.append(text)
        return paragraphs
    
    def extract_links(self, soup):
        links = []
        for tag in soup.find_all("a"):
            href = tag.get("href")
            if href:
                links.append(href)
        return links
    
    def extract_images(self, soup):
        images = []
        for tag in soup.find_all("img"):
            src = tag.get("src")
            if src:
                images.append(src)
        return images

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