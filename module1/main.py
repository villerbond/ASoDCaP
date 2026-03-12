from src.parser_manager import ParserManager

def main():
    html_file = "data/sample.html"
    manager = ParserManager()
    result = manager.process_file(html_file)
    print(result)

if __name__ == "__main__":
    main()