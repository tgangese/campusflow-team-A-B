import os

from campusflow.tickets import create_ticket, find_ticket
from campusflow.storage import load_tickets, save_tickets
from campusflow.workflow import assign_ticket, update_ticket_status
from campusflow.queue import get_open_tickets, get_assigned_tickets, sort_tickets_by_priority
from campusflow.cli import (
    menu_add_note,
    menu_view_notes,
    menu_search,
    menu_reports,
    menu_understanding_check,
    normalize_ticket_id,
)

DATA_PATH = os.path.join("data", "tickets.json")


def main():
    try:
        tickets = load_tickets(DATA_PATH)
    except ValueError as error:
        # Rejected load: leave the file untouched and do not start with bad data.
        print(f"Could not load {DATA_PATH}: {error}")
        print("Fix or move the file, then start again. Nothing was changed.")
        return
    print("=== CampusFlow Helpdesk - Final Project F1-F7 ===")
    
    while True:
        print("\n1. Create ticket (F1)")
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
        print("12. Save & Exit (F7)")
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            title = input("Title: ")
            category = input("Category (network/software/hardware/access/other): ")
            urgency = input("Urgency (low/medium/high): ")
            try:
                affected = int(input("Affected users: "))
                t = create_ticket(tickets, title, category, urgency, affected)
                print(f"Created {t['id']} priority={t['priority']}")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "2":
            if not tickets:
                print("No tickets")
            else:
                for t in tickets:
                    print(f"{t['id']} | {t['title']} | {t['priority']} | {t['status']} | assigned={t.get('assigned_to')}")
                
        elif choice == "3":
            tid = normalize_ticket_id(input("Ticket ID: "))
            t = find_ticket(tickets, tid)
            print(t if t else "Not found")
            
        elif choice == "4":
            tid = normalize_ticket_id(input("Ticket ID: "))
            staff = input("Assign to: ").strip()
            try:
                assign_ticket(tickets, tid, staff)
                print("Assigned")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "5":
            tid = normalize_ticket_id(input("Ticket ID: "))
            status = input("New status (open/in_progress/resolved): ").strip()
            try:
                update_ticket_status(tickets, tid, status)
                print("Status updated")
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == "6":
            open_t = get_open_tickets(tickets)
            sorted_t = sort_tickets_by_priority(open_t)
            print(f"--- OPEN QUEUE ({len(sorted_t)} tickets) sorted by priority ---")
            for t in sorted_t:
                print(f"{t['priority'].upper():8} | {t['id']} | {t['title']} | {t['affected_users']} users")
                
        elif choice == "7":
            menu_add_note(tickets)

        elif choice == "8":
            menu_search(tickets)

        elif choice == "9":
            menu_reports(tickets)

        elif choice == "10":
            menu_view_notes(tickets)

        elif choice == "11":
            menu_understanding_check(notes_path="data/understanding-notes.txt")

        elif choice == "12":
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            save_tickets(DATA_PATH, tickets)
            print(f"Saved {len(tickets)} tickets to {DATA_PATH}. Bye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 12.")

if __name__ == "__main__":
    main()
