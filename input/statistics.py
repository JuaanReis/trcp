import sqlite3
import questionary
from core.database.leads import get_statistics

def _show_count(label: str, count: int, total: int):
    percentage = count / total * 100 if total else 0
    print(f"{label:<24} {count:>6}  ({percentage:5.1f}%)")

def statistics():
    while True:
        print("\n[ Statistics ]\n")

        try:
            data = get_statistics()
        except sqlite3.Error as exc:
            print(f"Could not load statistics: {exc}")
            input("\nPress ENTER to continue...")
            return

        summary = data["summary"]
        total = summary["total"]

        print(f"Total saved:             {total}")
        print(f"Average score:           {summary['average_score']:.2f}")

        if not total:
            print("\nNo leads found yet.")
            input("\nPress ENTER to continue...")
            return

        option = questionary.select(
            "What would you like to view?",
            choices=[
                "Contact coverage",
                "By status",
                "By category",
                "Refresh",
                "Back to main menu",
            ],
        ).ask()

        if option is None or option == "Back to main menu":
            return

        if option == "Refresh":
            continue

        if option == "Contact coverage":
            print("\n[ Contact coverage ]\n")

            for label, key in [
                ("Website informed", "with_website"),
                ("Website not informed", "without_website"),
                ("Phone informed", "with_phone"),
                ("Phone not informed", "without_phone"),
                ("Website and phone", "with_both"),
                ("Neither informed", "without_contact"),
            ]:
                _show_count(label, summary[key], total)

        elif option == "By status":
            print("\n[ Leads by status ]\n")

            for item in data["statuses"]:
                _show_count(item["status"], item["total"], total)

        elif option == "By category":
            print("\n[ Leads by category ]\n")

            for category, count in data["categories"]:
                _show_count(category, count, total)

            print("\nA lead may appear in more than one category.")

        input("\nPress ENTER to continue...")