from .html_parser import HTMLParser
from .xml_parser import XMLParser
import os
import json
import csv

class ParserManager:

    """
    Класс, который управляет парсингом документов.
    - выбирает соответствующий парсер
    - управляет схемами
    - обрабатывает файли и папки с файлами
    - сохраняет результаты в форматы json и csv
    - ведет статистику обработки
    """

    def __init__(self, parser_type: str = "html.parser", schemas=None):

        self.html_parser = HTMLParser(parser_type)
        self.xml_parser = XMLParser()

        # Здесь пока только три схемы
        # Схемы используются для извлечения структурированных данных.
        # Одна схема - например, продукт или статья
        self.schemas = schemas if schemas is not None else {}

        self.stats = {
            "files_processed": 0,
            "files_failed": 0
        }

    def set_schemas(self, schemas):
        self.schemas = schemas

    # По расширению файла выбирает соответствующий парсер
    def get_parser(self, file_path):
        if file_path.endswith(".html"):
            return self.html_parser
        elif file_path.endswith(".xml"):
            return self.xml_parser
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    # Обработка одного файла
    def process_file(self, file_path: str, selected_schemas = None, data_options = None):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                toParse = f.read()

            parser = self.get_parser(file_path)

            # Если пользователь выбрал конкретные схемы, то оставляем только их
            if selected_schemas is not None:
                schemas_to_use = selected_schemas
            else:
                schemas_to_use = self.schemas

            # Пока XML парсер не поддерживает схемы
            if isinstance(parser, HTMLParser):
                result = parser.parse(toParse, schemas_to_use, data_options)
            else:
                result = parser.parse(toParse)
            
            self.stats["files_processed"] += 1
            
            return result

        except FileNotFoundError:
            print(f"Error: file '{file_path}' not found")
            self.stats["files_failed"] += 1
            return None
        except Exception as e:
            print(f"Error with {file_path}: {e}")
            self.stats["files_failed"] += 1
            return None
        
    # Обработка файлов в папке
    def process_directory(self, directory: str, selected_schemas = None, data_options = None):
        results = []

        if not os.path.isdir(directory):
            raise ValueError(f"{directory} is not a valid directory")

        self.stats = {
            "files_processed": 0,
            "files_failed": 0
        }

        for file in os.listdir(directory):
            if file.endswith(".html") or file.endswith(".xml"):
                path = os.path.join(directory, file)
                result = self.process_file(path, selected_schemas, data_options)
                if result:
                    results.append(result)

        print(f"\nProcessing complete:")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files failed: {self.stats['files_failed']}")
                    
        return results
    
    # Сохраняет данные в формате JSON
    def save_json(self, data, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Сохраняет данные в формате XSV
    def save_csv(self, data, file_path):

        if not data:
            print("No data to save")
            return
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        keys = data[0].keys()

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    # Возвращает текущую статистику
    def get_statistics(self):
        return self.stats.copy()