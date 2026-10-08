import json

def _build_query(
    selected: list[dict],
    bbox: tuple[float, float, float, float],
) -> str:
    south, west, north, east = bbox
    filters = dict.fromkeys(
        (item["key"], item["value"])
        for category in selected
        for item in category["filters"]
    )
    if not filters:
        raise ValueError("Categorias sem filtros")
    def quote(text: str) -> str:
        return json.dumps(text, ensure_ascii=False)
    statements = "\n".join(
        f"nwr({south},{west},{north},{east})"
        f'[{quote(key)}={quote(value)}]["name"];'
        for key, value in filters
    )
    return f"""[out:json][timeout:30];({statements});out tags;"""
