import re

def _phone_types(phone: str | None) -> set[str]:
    if not phone:
        return set()

    types = set()

    for number in re.split(r"[;/\n]+", phone):
        number = number.strip()
        digits = re.sub(r"\D", "", number)

        if not digits:
            continue

        if number.startswith("+"):
            if not digits.startswith("55"):
                types.add("unknown")
                continue

            digits = digits[2:]

        elif digits.startswith("0055"):
            digits = digits[4:]

        elif len(digits) in {12, 13} and digits.startswith("55"):
            digits = digits[2:]

        if len(digits) in {10, 11}:
            digits = digits[2:]

        if len(digits) == 9 and digits.startswith("9"):
            types.add("nine_digits")
        elif len(digits) == 8:
            types.add("eight_digits")
        else:
            types.add("unknown")

    return types

def matches_preferences(lead, preferences: dict) -> bool:
    has_website = bool((lead.website or "").strip())
    has_phone = bool((lead.phone or "").strip())

    website = preferences.get("website", "any")
    phone = preferences.get("phone", "any")

    if website == "present" and not has_website:
        return False

    if website == "missing" and has_website:
        return False

    if phone == "present":
        return has_phone

    if phone == "missing":
        return not has_phone

    if phone in {"nine_digits", "eight_digits"}:
        return phone in _phone_types(lead.phone)

    return True

def prioritize_leads(leads: list, preferences: dict) -> tuple[list, list]:
    preferred = []
    remaining = []

    for lead in leads:
        if matches_preferences(lead, preferences):
            preferred.append(lead)
        else:
            remaining.append(lead)

    return preferred, remaining