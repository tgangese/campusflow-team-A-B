"""CampusFlow - Auto-save version"""
import os
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_ticket_status
from campusflow.notes import add_note
from campusflow.search import search_tickets
from campusflow.reports import generate_report, format_report_text

TICKETS_PATH = "data/tickets.json"

def ensure_dir():
    os.makedirs(os.path.dirname(TICKETS_PATH), exist_ok=True)

def auto_save(tickets):
    ensure_dir()
    save_tickets(TICKETS_PATH, tickets)

def main():
    ensure_dir()
    try:
        tickets = load_tickets(TICKETS_PATH)
    except:
        tickets = []

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
            title = input("Title: ").strip()
            category = input("Category (Network/Hardware/Software/Other): ").strip()
            urgency = input("Urgency (low/medium/high): ").strip() or "medium"
            try:
                affected = int(input("Affected users: ").strip())
                t = create_ticket(tickets, title, category, urgency, affected)
                auto_save(tickets)
                print(f"Created {t['id']} - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            tid = input("Ticket ID: ").strip()
            staff = input("Staff name: ").strip()
            try:
                assign_ticket(tickets, tid, staff)
                auto_save(tickets)
                print(f"Assigned {tid} to {staff} - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            tid = input("Ticket ID: ").strip()
            new_status = input("New status (open/in_progress/resolved): ").strip()
            try:
                update_ticket_status(tickets, tid, new_status)
                auto_save(tickets)
                print(f"Status updated - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "7":
            tid = input("Ticket ID: ").strip()
            msg = input("Note message: ").strip()
            author = input("Author: ").strip() or "felix"
            try:
                add_note(tickets, tid, msg, author)
                auto_save(tickets)
                print("Note added - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "12":
            print("Bye!")
            break

if __name__ == "__main__":
    main()