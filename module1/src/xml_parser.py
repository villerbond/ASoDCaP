from bs4 import BeautifulSoup

class XMLParser:
    """
    Парсер для XML-документов.
    - извлекает элементы
    """
        
    def __init__(self):
        self.parser_type = "xml"

    def parse(self, xml: str):
        soup = BeautifulSoup(xml, self.parser_type)
        data = {
            "root": soup.find().name,
            "elements": self.extract_elements(soup)
        }
        return data

    def extract_elements(self, soup):
        elements = []
        for tag in soup.find_all():
            elements.append({
                "tag": tag.name,
                "text": tag.get_text(strip=True)
            })
        return elements