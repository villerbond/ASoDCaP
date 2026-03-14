product_schema = {
    "container": ("div", "product"),
    "fields": {
        "name": ("h2", None),
        "price": ("span", "price"),
        "rating": ("span", "rating")
    }
}

article_schema = {
    "container": ("article", None),
    "fields": {
        "title": ("h2", None),
        "author": ("span", "author"),
        "date": ("span", "date")
    }
}

avito_product_schema = {
    "container": ("div", "iva-item-content-fRmzq"),
    "fields": {
        "title": ("h2", "styles-module-root-KWbDd"),
        "price": ("span", "styles-module-size_l-kPWfk"),
        "condition": ("p", "stylesMarningNormal-module-paragraph-m-dense-mYuSK"),
    }
}

ALL_SCHEMAS = {
    "products": product_schema,
    "articles": article_schema,
    "avito_products": avito_product_schema
}

SCHEMA_NAMES = list(ALL_SCHEMAS.keys()) + ["all"]

def get_schemas(schema_names=None):
    if schema_names is None or "all" in schema_names:
        return ALL_SCHEMAS.copy()
    return {
        name: ALL_SCHEMAS[name]
        for name in schema_names
        if name in ALL_SCHEMAS
    }

def get_schema_choices():
    return SCHEMA_NAMES