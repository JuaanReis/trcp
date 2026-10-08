from time import perf_counter
from httpx import RequestError
from core.database.leads import save_leads
from core.lead.priority import prioritize_leads
from core.lead.service import search_businesses
from input.create_lead import prospecting_input
from output.lead_details import show_lead

def _show_results(title: str, leads: list):
    print(f"\n[ {title}: {len(leads)} ]\n")

    for index, lead in enumerate(leads, start=1):
        show_lead(lead, index)

def new_prospecting():
    print("\n[ New prospecting ]\n")

    try:
        search_data = prospecting_input()

        if search_data is None:
            print("\nProspecting canceled.")
            return

        preferences = search_data.pop("preferences", {})

        print("\nSearching businesses...")
        start = perf_counter()

        leads = search_businesses(**search_data)
        saved = save_leads(leads)

        print(f"\nTime: {perf_counter() - start:.2f}s")
        print(f"Found: {len(leads)}")
        print(f"Saved: {saved}")

        if not leads:
            print("\nNo businesses found.")
            return

        enabled = any(
            preferences.get(key, "any") != "any"
            for key in ("website", "phone")
        )

        if not enabled:
            _show_results("Results", leads)
            return

        preferred, remaining = prioritize_leads(leads, preferences)

        _show_results("Matching preferences", preferred)
        _show_results("Other results", remaining)

    except (
        RequestError,
        OSError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(f"\nProspecting failed: {exc}")

    finally:
        input("\nPress ENTER to continue...")