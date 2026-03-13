from .html_parser import HTMLParser
from .xml_parser import XMLParser
from schemas.schemas import product_schema, article_schema
import os
import json
import csv

class ParserManager:

    def __init__(self, parser_type: str = "html.parser"):

        self.html_parser = HTMLParser(parser_type)
        self.xml_parser = XMLParser()

        self.schemas = [
            ("products", product_schema), 
            ("articles", article_schema)
        ]

    def get_parser(self, file):
        if file.endswith(".html"):
            return self.html_parser
        elif file.endswith(".xml"):
            return self.xml_parser
        else:
            raise ValueError(f"Unsupported file format: {file}")

    def process_file(self, file: str):

        try:
            with open(file, "r", encoding="utf-8") as f:
                toParse = f.read()
        except FileNotFoundError:
            print(f"Error: file '{file}' not found")
            return None
        except Exception as e:
            print(f"Error with reading file: {e}")
            return None
        
        parser = self.get_parser(file)
        
        if isinstance(parser, HTMLParser):
            result = parser.parse(toParse, self.schemas)
        else:
            result = parser.parse(toParse)
            
        return result
    

    def process_directory(self, directory: str):
        results = []

        if not os.path.isdir(directory):
            raise ValueError(f"{directory} is not a valid directory")

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
            print("No data to save")
            return
        
        keys = data[0].keys()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)