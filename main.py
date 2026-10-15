"""CampusFlow - Full version - silent auto-save"""
import os
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket, find_ticket
from campusflow.workflow import assign_ticket, update_ticket_status
from campusflow.notes import add_note
from campusflow.queue import get_open_tickets, sort_by_priority
from campusflow.search import search_tickets
from campusflow.reports import generate_report, format_report_text

TICKETS_PATH = "data/tickets.json"

def ensure_dir():
    os.makedirs(os.path.dirname(TICKETS_PATH), exist_ok=True)

def auto_save(tickets):
    ensure_dir()
    save_tickets(TICKETS_PATH, tickets)

def normalize_id(raw):
    return raw.strip().upper() if isinstance(raw, str) else raw

try:
    from campusflow.understanding_check import run_quiz
except:
    def run_quiz():
        print("Understanding Check not available")

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
            if title.lower() == "cancel": continue
            category = input("Category (Network/Hardware/Software/Other): ").strip()
            if category.lower() == "cancel": continue
            urgency = input("Urgency (low/medium/high): ").strip() or "medium"
            if urgency.lower() == "cancel": continue
            affected_raw = input("Affected users: ").strip()
            if affected_raw.lower() == "cancel": continue
            try:
                affected = int(affected_raw)
                t = create_ticket(tickets, title, category, urgency, affected)
                auto_save(tickets)
                print(f"Created {t['id']}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            if not tickets:
                print("No tickets yet")
            else:
                for t in tickets:
                    assigned = t.get('assigned_to') or "Unassigned"
                    print(f"{t['id']}: {t['title']} | {t['category']} | {t['priority']} | {t['status']} | {assigned}")

        elif choice == "3":
            raw = input("Ticket ID: ").strip()
            t = find_ticket(tickets, raw)
            if not t:
                print(f"Ticket '{raw}' not found")
            else:
                print(f"\n--- {t['id']} ---")
                print(f"Title: {t['title']}")
                print(f"Category: {t['category']} | Urgency: {t['urgency']} | Priority: {t['priority']}")
                print(f"Status: {t['status']} | Affected: {t['affected_users']} | Assigned to: {t.get('assigned_to') or 'None'}")

        elif choice == "4":
            raw = input("Ticket ID: ").strip()
            staff = input("Staff name: ").strip()
            try:
                assign_ticket(tickets, normalize_id(raw), staff)
                auto_save(tickets)
                print(f"Assigned {normalize_id(raw)} to {staff}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            raw = input("Ticket ID: ").strip()
            status = input("New status (open/in_progress/resolved): ").strip()
            try:
                update_ticket_status(tickets, normalize_id(raw), status)
                auto_save(tickets)
                print(f"Status updated")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            open_t = get_open_tickets(tickets)
            sorted_t = sort_by_priority(open_t)
            if not sorted_t:
                print("No open tickets")
            else:
                for t in sorted_t:
                    print(f"{t['id']}: {t['title']} [{t['priority']}]")

        elif choice == "7":
            raw = input("Ticket ID: ").strip()
            msg = input("Note message: ").strip()
            author = input("Author: ").strip() or "felix"
            try:
                add_note(tickets, normalize_id(raw), msg, author)
                auto_save(tickets)
                print(f"Note added to {normalize_id(raw)}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":
            kw = input("Search keyword (blank shows all, searches title + notes): ").strip()
            results = search_tickets(tickets, kw)
            if not results:
                print(f"No tickets found for '{kw}'")
            else:
                print(f"Found {len(results)} ticket(s):")
                for r in results:
                    assigned = r.get('assigned_to') or "Unassigned"
                    print(f"  {r['id']}: {r['title']} | {r['priority']} | {r['status']} | {assigned}")

        elif choice == "9":
            report = generate_report(tickets)
            print(format_report_text(report))

        elif choice == "10":
            raw = input("Ticket ID: ").strip()
            t = find_ticket(tickets, raw)
            if not t:
                print(f"Ticket '{raw}' not found")
            else:
                notes = t.get("notes", [])
                if not notes:
                    print(f"{t['id']} has no notes")
                else:
                    for n in notes:
                        print(f"{n.get('note_id')} | {n.get('author')}: {n.get('message')}")

        elif choice == "11":
            run_quiz()

        elif choice == "12":
            print("Bye!")
            break

if __name__ == "__main__":
    main()