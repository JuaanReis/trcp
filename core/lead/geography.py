import math

def _validate_bbox(bbox) -> tuple[float, float, float, float]:
    try:
        south, west, north, east = map(float, bbox)
    except (TypeError, ValueError):
        raise ValueError(
            "bbox deve conter quatro números: sul, oeste, norte, leste"
        ) from None
    if not (
        all(math.isfinite(v) for v in (south, west, north, east))
        and -90 <= south < north <= 90
        and -180 <= west < east <= 180
    ):
        raise ValueError("bbox inválido: use sul, oeste, norte, leste")
    return south, west, north, east

def split_regions(city, state, bbox, parts):
    if not isinstance(parts, int) or isinstance(parts, bool) or parts < 1:
        raise ValueError("parts precisa ser um inteiro positivo")
    south, west, north, east = _validate_bbox(bbox)
    height = (north - south) / parts
    return [{"city": city, "state": state, "bbox": (
        south + i * height, west,
        north if i == parts - 1 else south + (i + 1) * height, east
    )} for i in range(parts)]
