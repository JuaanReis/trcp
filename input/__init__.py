import questionary
from core.database.leads import init_db, list_leads
from input.new_prospecting import new_prospecting
from output.ui import banner
from input.search_lead import search_lead
from input.my_leads import my_leads
from input.statistics import statistics
from input.export_leads import export_leads
from os import system

init_db()

def main_menu():
    banner()
    while True:

        option = questionary.select(
            "What would you like to do?",
            choices=[
                "New prospecting",
                "My leads",
                "Search lead",
                "Export leads",
                "Statistics",
                "Exit"
            ]
        ).ask()

        if option == "New prospecting":
            new_prospecting()
            system("cls")
            banner()

        elif option == "My leads":
            my_leads(list_leads())
            input("\nPress ENTER to continue...")
            system("cls")
            banner()

        elif option == "Search lead":
            search_lead()
            system("cls")
            banner()

        elif option == "Export leads":
            export_leads()
            system("cls")
            banner()

        elif option == "Statistics":
            statistics()
            system("cls")
            banner()

        elif option == "Exit" or option is None:
            print("\nExiting TRCP...")
            system("cls")
            break