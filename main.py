"""CampusFlow Helpdesk - Final Project F1-F7 - Professional + silent auto-save"""
import os
from campusflow.storage import load_tickets, save_tickets
from campusflow.cli import (
    menu_add_note,
    menu_assign_ticket,
    menu_create_ticket,
    menu_reports,
    menu_search,
    menu_update_status,
    menu_view_notes,
    menu_view_ticket,
    menu_understanding_check,
)
from campusflow.queue import get_open_tickets, sort_by_priority

TICKETS_PATH = "data/tickets.json"
NOTES_PATH = "data/understanding_notes.txt"

def ensure_dir():
    os.makedirs(os.path.dirname(TICKETS_PATH), exist_ok=True)

def auto_save(tickets):
    ensure_dir()
    save_tickets(TICKETS_PATH, tickets)

def load_tickets_safe():
    try:
        from campusflow.storage import load_tickets as lt
        return lt(TICKETS_PATH)
    except:
        return []

def main():
    ensure_dir()
    tickets = load_tickets_safe()

    while True:
        print("\n=== CampusFlow Helpdesk - Final Project F1-F7 ===")
        print("1. Create ticket (F1)")
        print("2. List tickets (F2)")
        print("3. View ticket (F2)")
        print("4. Assign ticket (F3)")
        print("5. Update status (F4)")
        print("6. Show priority queue (F5)")
        print("7. Add follow-up note")
        print("8. Search tickets")
        print("9. Reports")
        print("10. View ticket notes")
        print("11. Engineering Understanding Check")
        print("12. Exit (F7)")

        choice = input("Choice: ").strip()

        if choice == "1":
            result = menu_create_ticket(tickets, input, print)
            if result:
                auto_save(tickets)  # silent auto-save, no extra text

        elif choice == "2":
            if not tickets:
                print("No tickets available. Create a ticket first using option 1.")
            else:
                print(f"--- Ticket List ({len(tickets)} total) ---")
                for t in tickets:
                    assigned = t.get('assigned_to') or "Unassigned"
                    print(f"{t['id']} | {t['title']} | {t['category']} | {t['priority']} | {t['status']} | {assigned}")

        elif choice == "3":
            menu_view_ticket(tickets, input, print)

        elif choice == "4":
            result = menu_assign_ticket(tickets, input, print)
            if result:
                auto_save(tickets)

        elif choice == "5":
            result = menu_update_status(tickets, input, print)
            if result:
                auto_save(tickets)

        elif choice == "6":
            open_t = get_open_tickets(tickets)
            sorted_t = sort_by_priority(open_t)
            if not sorted_t:
                print("No open tickets in priority queue.")
            else:
                print(f"--- Priority Queue ({len(sorted_t)} open) ---")
                for t in sorted_t:
                    print(f"{t['id']} | {t['title']} | {t['priority']} | {t['status']}")

        elif choice == "7":
            result = menu_add_note(tickets, input, print)
            if result:
                auto_save(tickets)

        elif choice == "8":
            menu_search(tickets, input, print)

        elif choice == "9":
            menu_reports(tickets, print)

        elif choice == "10":
            menu_view_notes(tickets, input, print)

        elif choice == "11":
            menu_understanding_check(input, print, NOTES_PATH)

        elif choice == "12":
            print("Exiting CampusFlow. Goodbye!")
            break

        else:
            if choice == "":
                print("Error: Choice cannot be blank. Please enter a number from 1 to 12.")
            else:
                print(f"Error: Invalid choice '{choice}'. Please enter a number from 1 to 12.")

if __name__ == "__main__":
    main()