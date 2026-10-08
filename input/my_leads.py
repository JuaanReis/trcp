import questionary
from questionary import Choice
from output.lead_details import show_lead

def my_leads(leads: list):
    print("\n[ My leads ]\n")
    if not leads:
        print("No leads found yet.")
        input("\nPress ENTER to continue...")
        return
    while True:
        selected = questionary.select(
            f"Select a lead ({len(leads)} available):",
            choices=[Choice(f"{i}. {lead.name} | {lead.category}", value=i-1)
                     for i, lead in enumerate(leads, 1)]
                    + [Choice("Back to main menu", value="back")],
        ).ask()
        if selected is None or selected == "back":
            return
        print("\n[ Lead details ]\n")
        show_lead(leads[selected])
        input("\nPress ENTER to continue...")
