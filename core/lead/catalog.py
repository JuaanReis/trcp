import json
import unicodedata
from pathlib import Path

CATALOG_PATH = Path(__file__).with_name("categories.json")

def _normalize(text: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(character)
    ).strip()

def load_categories(path=CATALOG_PATH) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def suggest_categories(
    text: str = "",
    limit: int = 20,
    *,
    catalog_path=CATALOG_PATH,
) -> list[dict]:
    if limit < 1:
        raise ValueError("limit precisa ser positivo")
    words = _normalize(text).split()
    matches = []
    for category in load_categories(catalog_path):
        searchable = _normalize(
            " ".join([
                category["id"],
                category["label"],
                category["group"],
                *category["keywords"],
            ])
        )
        if all(word in searchable for word in words):
            matches.append(category)
    matches.sort(key=lambda item: _normalize(item["label"]))
    return matches[:limit]

def _select_categories(
    categories: str | list[str],
    catalog_path,
) -> list[dict]:
    if isinstance(categories, str):
        categories = [categories]
    if not categories:
        raise ValueError("Selecione pelo menos uma categoria")
    catalog = {
        category["id"]: category
        for category in load_categories(catalog_path)
    }
    unknown = [
        category_id
        for category_id in categories
        if category_id not in catalog
    ]
    if unknown:
        raise ValueError(f"Categorias desconhecidas: {unknown}")
    return [
        catalog[category_id]
        for category_id in dict.fromkeys(categories)
    ]
