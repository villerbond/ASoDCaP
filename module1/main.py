from src.parser_manager import ParserManager
import json

def main():
    html_file = "data/sample.html"
    manager = ParserManager()
    result = manager.process_file(html_file)
    print(result)
    with open("output/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()