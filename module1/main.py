import argparse
import os
from src.parser_manager import ParserManager

def main():

    """
    Обрабатываем аргументы командной строки, управляем процессом парсинга
    и сохраняем результаты в указанном формате
    """

    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(epilog="""
        Examples:
        # Базовое использование
        python main.py sample.html --format json
        # Только структурированные данные
        python main.py sample.html --structured-only
        # Только общие данные (заголовки, ссылки, картинки)
        python main.py sample.html --common-only
        # Выбрать конкретные типы данных
        python main.py sample.html --data-types headings links tables
        # Полный парсинг (все данные)
        python main.py sample.html --all-data
        # Визуализация DOM-дерева документа
        python main.py sample.html --visualize
        # Обработка всех файлов в директории
        python main.py ./data --format csv
        # Обработка XML-файла
        python main.py sample.xml --format json
        # Выбор конкретных схем для обработки
        python main.py sample.html --schemas products articles --format csv
    """)

    parser.add_argument("path", help="Path to HTML/XML file or directory")
    parser.add_argument("--format", choices=["json", "csv"], 
                        help="Export format (JSON or CSV)")
    data_group = parser.add_mutually_exclusive_group()
    data_group.add_argument("--all-data", action="store_true",
                            help="Parse all data (default)")
    data_group.add_argument("--structured-only", action="store_true",
                            help="Only structured data (by schemas)")
    data_group.add_argument("--common-only", action="store_true",
                            help="Only commot data (headings, links, images)")
    data_group.add_argument("--data-types", nargs="+",
                            choices=["metadata", "headings", "paragraphs", "links",
                                     "images", "tables", "lists", "metrics", "dom"],
                            help="What data to parse")
    parser.add_argument("--visualize", action="store_true",
                        help="Visualize DOM tree sctructure")
    parser.add_argument("--output-dir", default="output", 
                        help="Output directory for results (default: output/)")
    parser.add_argument("--schemas", nargs="+",
                        choices=["products", "articles", "avito_products", "all"],
                        default=["all"],
                        help="Specific schemas to extract")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    manager = ParserManager()

    data_options = {
        "all": args.all_data or not 
            (args.structured_only or args.common_only or args.data_types),
        "structured_only": args.structured_only,
        "common_only": args.common_only,
        "data_types": args.data_types or []
    }

    # Фильтрация схем
    if args.schemas != ["all"]:
        selected_schemas = {name: manager.schemas[name] 
                            for name in args.schemas 
                            if name in manager.schemas}
    else:
        selected_schemas = manager.schemas

    # Рассматриваем два случая: когда передан один файл или когда передана папка
    if os.path.isfile(args.path):
        results = [manager.process_file(args.path, selected_schemas, data_options)]
        source_name = os.path.basename(args.path).split('.')[0]
    else:
        results = manager.process_directory(args.path, selected_schemas, data_options)
        source_name = "directory"

    if not results or not any(results):
        print("No data to process")
        return

    # Далее по всем полученным результатам обрабатываем каждый 
    # (либо экспортируем, либо визуализируем)
    for i, result in enumerate(results):

        if not result:
            continue

        number = f"_{i}" if len(results) > 1 else ""

        if args.visualize:
            if result['dom_tree'] and 'dom_tree' in result:
                print(f"\nDOM TREE OF DOCUMENT {i+1}:\n")
                manager.html_parser.visualize_dom_tree(result["dom_tree"])

        if args.format == "json":
            output_file = os.path.join(args.output_dir, f"{source_name}{number}.json")
            manager.save_json(result, output_file)
            print(f"JSON saved to: {output_file}")
        
        elif args.format == "csv":
            for section in ["products", "articles", "avito_products", "headings", "metrics"]:
                if section in result and result[section]:
                    output_file = os.path.join(args.output_dir, f"{source_name}{number}_{section}.csv")

                    if section in ["products", "articles", "avito_products"]:
                        manager.save_csv(result[section], output_file)
                    else:
                        manager.save_csv([result[section]], output_file)
                    print(f"CSV saved to: {output_file}")

if __name__ == "__main__":
    main()