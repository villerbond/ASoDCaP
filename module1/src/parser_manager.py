class ParserManager:
    def __init__(self, parser):
        self.parser = parser
    def process_file(self, file):
        with open(file, "r", encoding="utf-8") as f:
            html = f.read()
        result = self.parser.parse(html)
        return result