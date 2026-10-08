import math
import questionary
from questionary import Choice
from core.lead.search import suggest_categories
from conf import config

system = config["system"]

def _required(value: str):
    return bool(value.strip()) or "Preencha este campo."

def _validate_bbox(value: str):
    try:
        south, west, north, east = [
            float(item.strip())
            for item in value.split(",")
        ]
    except ValueError:
        return "Informe quatro números: sul, oeste, norte, leste."

    if not (
        all(math.isfinite(v) for v in (south, west, north, east))
        and -90 <= south < north <= 90
        and -180 <= west < east <= 180
    ):
        return "Coordenadas inválidas ou fora de ordem."

    return True

def priority_input() -> dict | None:
    enabled = questionary.confirm(
        "Configure optional result priorities?",
        default=False,
    ).ask()

    if enabled is None:
        return None

    if not enabled:
        return {
            "website": "any",
            "phone": "any",
        }

    website = questionary.select(
        "Website preference:",
        choices=[
            Choice("No preference", value="any"),
            Choice("Website informed first", value="present"),
            Choice("Website not informed first", value="missing"),
        ],
    ).ask()

    if website is None:
        return None

    phone = questionary.select(
        "Phone preference:",
        choices=[
            Choice("No preference", value="any"),
            Choice("Phone informed first", value="present"),
            Choice("Phone not informed first", value="missing"),
            Choice(
                "9 digits starting with 9 first",
                value="nine_digits",
            ),
            Choice(
                "8 digits (landline or older format) first",
                value="eight_digits",
            ),
        ],
    ).ask()

    if phone is None:
        return None

    return {
        "website": website,
        "phone": phone,
    }

def prospecting_input() -> dict | None:
    preferences = priority_input()

    if preferences is None:
        return None

    selected = {}

    while True:
        term = questionary.text(
            "Search categories (blank shows all):",
        ).ask()

        if term is None:
            return None

        suggestions = suggest_categories(term, limit=1000)

        if not suggestions:
            print("\nNo categories found. Try another term.\n")
            continue

        category_ids = questionary.checkbox(
            "Select categories:",
            choices=[
                Choice(
                    title=f"{item['label']} [{item['id']}]",
                    value=item["id"],
                    checked=item["id"] in selected,
                )
                for item in suggestions
            ],
            instruction="(SPACE selects; ENTER confirms)",
        ).ask()

        if category_ids is None:
            return None

        for item in suggestions:
            selected.pop(item["id"], None)

        by_id = {item["id"]: item for item in suggestions}

        for category_id in category_ids:
            selected[category_id] = by_id[category_id]

        print("\nSelected categories:")
        for item in selected.values():
            print(f"  - {item['label']}")

        action = questionary.select(
            "Next step:",
            choices=[
                Choice("Search more categories", value="search"),
                Choice(
                    "Continue",
                    value="continue",
                    disabled=None if selected else "Select a category first",
                ),
                Choice("Cancel", value="cancel"),
            ],
        ).ask()

        if action is None or action == "cancel":
            return None

        if action == "continue":
            break

    city = questionary.text(
        "City:",
        default="São Paulo",
        validate=_required,
    ).ask()

    if city is None:
        return None

    state = questionary.text(
        "State:",
        default="São Paulo",
        validate=_required,
    ).ask()

    if state is None:
        return None

    print("\nThe coordinates determine the search area.")
    print("City and state are labels for the results.")

    bbox_text = questionary.text(
        "Bounding box (south, west, north, east):",
        default=system['bounding_box'],
        validate=_validate_bbox,
    ).ask()

    if bbox_text is None:
        return None

    mode = questionary.select(
        "Search mode:",
        choices=[
            Choice(
                f"Parallel: {system['parts']} regions / {system['threads']} threads",
                value="parallel",
            ),
            Choice(
                "Single request",
                value="single",
            ),
        ],
    ).ask()

    if mode is None:
        return None

    return {
        "categories": list(selected),
        "city": city.strip(),
        "state": state.strip(),
        "bbox": tuple(
            float(item.strip())
            for item in bbox_text.split(",")
        ),
        "parts": int(system["parts"]) if mode == "parallel" else 1,
        "max_workers": int(system["threads"]) if mode == "parallel" else 1,
        "preferences": preferences,
    }