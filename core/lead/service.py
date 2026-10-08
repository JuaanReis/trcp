from concurrent.futures import ThreadPoolExecutor, as_completed
from .catalog import CATALOG_PATH, _select_categories
from .geography import _validate_bbox, split_regions
from .query import _build_query
from .transport import _request_overpass
from .mapping import _create_leads

def search_regions(
    categories: str | list[str],
    regions: list[dict],
    max_workers: int = 2,
    *,
    catalog_path=CATALOG_PATH,
) -> list:
    if not isinstance(max_workers, int) or isinstance(max_workers, bool) or max_workers < 1:
        raise ValueError("max_workers precisa ser positivo")
    if not regions:
        raise ValueError("Informe pelo menos uma região")
    selected = _select_categories(categories, catalog_path)
    prepared = []
    for region in regions:
        city = region["city"].strip()
        state = region["state"].strip()
        if not city or not state:
            raise ValueError("Informe cidade e estado")
        
        prepared.append({
            "city": city,
            "state": state,
            "bbox": _validate_bbox(region["bbox"]),
        })

    batches = [None] * len(prepared)
    with ThreadPoolExecutor(
        max_workers=min(max_workers, len(prepared))

    ) as executor:
        futures = {
            executor.submit(
                _request_overpass,
                _build_query(selected, region["bbox"]),
            ): index
            for index, region in enumerate(prepared)
        }

        for future in as_completed(futures):
            index = futures[future]
            region = prepared[index]
            try:
                elements = future.result()
            except Exception as exc:
                for pending in futures:
                    pending.cancel()
                raise RuntimeError(
                    f"Falha na região {region['bbox']}: {exc}"
                ) from exc
            batches[index] = (region, elements)
    return _create_leads(batches, selected)

def search_businesses(categories: str | list[str], city: str, state: str,
                      bbox: tuple[float, float, float, float], *,
                      max_workers: int = 5, parts: int = 5,
                      catalog_path=CATALOG_PATH) -> list:
    
    regions = split_regions(city, state, bbox, parts)
    return search_regions(categories, regions, max_workers=max_workers,
                          catalog_path=catalog_path)

