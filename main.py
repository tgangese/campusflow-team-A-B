"""CampusFlow - Full version with Auto-save on assign and notes"""
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

# Compatibility import for understanding check
try:
    from campusflow.understanding_check import run_quiz
except ImportError:
    try:
        from campusflow.cli import run_understanding_check as run_quiz
    except:
        def run_quiz():
            print("Understanding Check not found")

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
            if title.lower() == "cancel":
                continue
            category = input("Category (Network/Hardware/Software/Other): ").strip()
            if category.lower() == "cancel":
                continue
            urgency = input("Urgency (low/medium/high): ").strip() or "medium"
            if urgency.lower() == "cancel":
                continue
            affected_raw = input("Affected users: ").strip()
            if affected_raw.lower() == "cancel":
                continue
            try:
                affected = int(affected_raw)
                t = create_ticket(tickets, title, category, urgency, affected)
                auto_save(tickets)
                print(f"Created {t['id']} [{t['priority']}] - auto-saved to {TICKETS_PATH}")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            if not tickets:
                print("No tickets")
            else:
                for t in tickets:
                    print(f"{t['id']}: {t['title']} | {t['category']} | {t['priority']} | {t['status']} | assigned_to={t['assigned_to']}")

        elif choice == "3":
            tid = input("Ticket ID: ").strip()
            t = find_ticket(tickets, tid.upper())
            if not t:
                t = find_ticket(tickets, tid)
            if not t:
                print(f"Ticket {tid} not found")
            else:
                print(t)

        elif choice == "4":
            tid = input("Ticket ID: ").strip()
            if tid.lower() == "cancel":
                continue
            staff = input("Staff name: ").strip()
            if staff.lower() == "cancel":
                continue
            try:
                assign_ticket(tickets, tid, staff)
                auto_save(tickets)
                print(f"Assigned {tid.upper()} to {staff} - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            tid = input("Ticket ID: ").strip()
            if tid.lower() == "cancel":
                continue
            status = input("New status (open/in_progress/resolved): ").strip()
            if status.lower() == "cancel":
                continue
            try:
                update_ticket_status(tickets, tid, status)
                auto_save(tickets)
                print(f"Status updated to {status} - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":
            try:
                open_t = get_open_tickets(tickets)
                sorted_t = sort_by_priority(open_t)
                if not sorted_t:
                    print("No open tickets")
                else:
                    for t in sorted_t:
                        print(f"{t['id']}: {t['title']} [{t['priority']}]")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "7":
            tid = input("Ticket ID: ").strip()
            if tid.lower() == "cancel":
                continue
            msg = input("Note message: ").strip()
            if msg.lower() == "cancel":
                continue
            author = input("Author: ").strip() or "felix"
            if author.lower() == "cancel":
                continue
            try:
                add_note(tickets, tid, msg, author)
                auto_save(tickets)
                print("Note added - auto-saved")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":
            kw = input("Search keyword (blank for all): ").strip()
            results = search_tickets(tickets, kw)
            if not results:
                print("No results")
            else:
                print(f"Found {len(results)}:")
                for r in results:
                    print(f"  {r['id']}: {r['title']}")

        elif choice == "9":
            try:
                report = generate_report(tickets)
                print(format_report_text(report))
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "10":
            tid = input("Ticket ID: ").strip()
            t = find_ticket(tickets, tid.upper()) or find_ticket(tickets, tid)
            if not t:
                print("Ticket not found")
            else:
                notes = t.get("notes", [])
                if not notes:
                    print("No notes")
                else:
                    for n in notes:
                        print(f"{n.get('note_id')}: {n.get('author')}: {n.get('message')}")

        elif choice == "11":
            run_quiz()

        elif choice == "12":
            print("Bye!")
            break

        else:
            if choice == "":
                continue
            print("Invalid choice")

if __name__ == "__main__":
    main()