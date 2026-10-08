import re
import sqlite3
import unicodedata
import questionary
from questionary import Choice
from prompt_toolkit.completion import Completer, Completion
from core.database.leads import list_leads
from output.lead_details import show_lead

def _normalize(text):
    return "".join(
        character
        for character in unicodedata.normalize(
            "NFKD", str(text or "").casefold()
        )
        if not unicodedata.combining(character)
    ).strip()

def _has_text(value):
    return bool(str(value or "").strip())

def _has_instagram(lead):
    return any(
        _has_text(profile)
        for profile in (lead.social_profiles or [])
    )

def _local_phone_numbers(phone):
    numbers = []

    for part in re.split(r"[;\n]+", str(phone or "")):
        digits = re.sub(r"\D", "", part)

        if digits.startswith("0055") and len(digits) in (14, 15):
            digits = digits[4:]

        elif digits.startswith("55") and len(digits) in (12, 13):
            digits = digits[2:]

        if len(digits) in (10, 11):
            digits = digits[2:]

        if len(digits) in (8, 9):
            numbers.append(digits)

    return numbers

def _filter_input():
    specifications = [
        (
            "website",
            "Website filter:",
            [
                Choice("Any", value="any"),
                Choice("Website informed", value="present"),
                Choice("Website not informed", value="missing"),
            ],
        ),
        (
            "phone",
            "Phone filter:",
            [
                Choice("Any", value="any"),
                Choice("Phone informed", value="present"),
                Choice("Phone not informed", value="missing"),
                Choice("9 digits starting with 9", value="nine"),
                Choice("8 digits", value="eight"),
            ],
        ),
        (
            "instagram",
            "Instagram filter:",
            [
                Choice("Any", value="any"),
                Choice("Instagram informed", value="present"),
                Choice("Instagram not informed", value="missing"),
            ],
        ),
    ]

    filters = {}

    for key, message, choices in specifications:
        value = questionary.select(
            message,
            choices=choices,
        ).ask()

        if value is None:
            return None

        filters[key] = value

    return filters

def _matches(lead, filters):
    website = _has_text(lead.website)
    phone = _has_text(lead.phone)
    instagram = _has_instagram(lead)

    for key, present in (
        ("website", website),
        ("phone", phone),
        ("instagram", instagram),
    ):
        preference = filters.get(key, "any")

        if preference == "present" and not present:
            return False

        if preference == "missing" and present:
            return False

    phone_filter = filters.get("phone", "any")

    if phone_filter in ("nine", "eight"):
        numbers = _local_phone_numbers(lead.phone)

        if phone_filter == "nine":
            return any(
                len(number) == 9 and number.startswith("9")
                for number in numbers
            )

        return any(len(number) == 8 for number in numbers)

    return True


class LeadCompleter(Completer):
    def __init__(self, options):
        self.options = options

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = _normalize(text).replace("@", "").split()

        for label, lead in self.options.items():
            instagram = ", ".join(lead.social_profiles or [])

            searchable = _normalize(
                f"{lead.name} {lead.category} {lead.location} "
                f"{lead.phone or ''} {lead.website or ''} {instagram}"
            ).replace("@", "")

            if all(word in searchable for word in words):
                yield Completion(
                    text=label,
                    start_position=-len(text),
                    display=lead.name,
                    display_meta=(
                        f"{lead.category} | {lead.location} | "
                        f"Phone: {lead.phone or 'Not informed'} | "
                        f"Instagram: {instagram or 'Not informed'}"
                    ),
                )

def _search_filtered(leads):
    options = {
        f"{lead.name} | {lead.category} | {lead.location} [#{index}]": lead
        for index, lead in enumerate(leads, start=1)
    }

    completer = LeadCompleter(options)

    while True:
        selected = questionary.autocomplete(
            "Search a lead (blank returns):",
            choices=list(options),
            completer=completer,
            validate=lambda value: (
                not value.strip()
                or value in options
                or "Select a lead from the suggestions."
            ),
        ).ask()

        if selected is None or not selected.strip():
            return

        print("\n[ Lead details ]\n")
        show_lead(options[selected])
        input("\nPress ENTER to continue...")

def search_lead():
    print("\n[ Search lead ]\n")

    try:
        leads = list_leads()

        if not leads:
            print("No leads found yet.")
            input("\nPress ENTER to continue...")
            return

        filtered = leads

        while True:
            action = questionary.select(
                f"Matching leads: {len(filtered)} / {len(leads)}",
                choices=[
                    Choice("Search matching leads", value="search"),
                    Choice("Show all matching leads", value="list"),
                    Choice("Configure filters", value="filters"),
                    Choice("Clear filters", value="clear"),
                    Choice("Back to main menu", value="back"),
                ],
            ).ask()

            if action is None or action == "back":
                return

            if action == "filters":
                filters = _filter_input()

                if filters is not None:
                    filtered = [
                        lead for lead in leads
                        if _matches(lead, filters)
                    ]

                continue

            if action == "clear":
                filtered = leads
                continue

            if not filtered:
                print("\nNo leads match these filters.")
                input("\nPress ENTER to continue...")
                continue

            if action == "search":
                _search_filtered(filtered)

            elif action == "list":
                print(f"\n[ Matching leads: {len(filtered)} ]\n")

                for index, lead in enumerate(filtered, start=1):
                    show_lead(lead, index)

                input("\nPress ENTER to continue...")

    except (sqlite3.Error, OSError, ValueError) as exc:
        print(f"Could not load leads: {exc}")
        input("\nPress ENTER to continue...")