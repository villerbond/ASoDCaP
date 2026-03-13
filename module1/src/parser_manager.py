from .html_parser import HTMLParser
from schemas.schemas import product_schema
import os
import json
import csv

class ParserManager:

    def __init__(self, parser_type: str = "html.parser"):
        
        self.parser = HTMLParser(parser_type)
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
    

    def process_directory(self, directory: str):
        results = []

        for file in os.listdir(directory):
            if file.endswith(".html"):
                path = os.path.join(directory, file)
                result = self.process_file(path)
                if result:
                    results.append(result)
                    
        return results
    
    def save_json(self, data, path):

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_csv(self, data, path):

        if not data:
            return
        
        keys = data[0].keys()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)