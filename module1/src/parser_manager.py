from .html_parser import HTMLParser
from schemas.schemas import product_schema

class ParserManager:

    def __init__(self):
        self.parser = HTMLParser()
        self.schemas = [("products", product_schema)]

    def process_file(self, file: str):

        try:
            with open(file, "r", encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            print(f"Error: file '{file}' not found")
            return None
        except Exception as e:
            print(f"Error with reading file: {e}")
            return None
        
        result = self.parser.parse(html, self.schemas)
        return result