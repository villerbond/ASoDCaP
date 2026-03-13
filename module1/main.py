import argparse
from src.parser_manager import ParserManager

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="Path to HTML/XML file or directory")
    parser.add_argument("--format", choices=["json", "csv"], help="Export format")
    parser.add_argument("--visualize", action="store_true",help="Visualize DOM tree")

    args = parser.parse_args()

    manager = ParserManager()

    if args.path.endswith(".html") or args.path.endswith(".xml"):
        result = manager.process_file(args.path)
    else:
        result = manager.process_directory(args.path)

    if not result:
        return
    
    if args.visualize:
        if isinstance(result, dict) and 'dom_tree' in result:
            print("\nDOM TREE OF DOCUMENT:\n")
            manager.html_parser.visualize_dom_tree(result["dom_tree"])
        else:
            print("DOM visualization available only from HTML documents")

    if args.format == "json":
        manager.save_json(result, "output/result.json")
    elif args.format == "csv":
        if isinstance(result, dict) and "products" in result:
            manager.save_csv(result["products"], "output/products.csv")
        else:
            print("CSV export only for structured data")

if __name__ == "__main__":
    main()