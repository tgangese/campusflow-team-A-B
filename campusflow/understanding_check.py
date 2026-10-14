"""Engineering Understanding Check - CampusFlow Next (Engineer B).

Two parts:
  1. run_understanding_check() -> dict   written explanation of our rules.
  2. The interactive 6-question quiz. The QUESTION_BANK (data) is kept
     separate from score_answers (logic) and from run_quiz (menu loop).
"""

VALID_CHOICES = ("A", "B", "C", "D")


def run_understanding_check():
    """Return a plain-language explanation of CampusFlow's core rules."""
    return {
        "priority_rules": (
            "Priority is calculated from urgency and affected_users, checked "
            "in this order: critical = high urgency AND affected_users >= 10; "
            "otherwise high = high urgency OR affected_users >= 10; otherwise "
            "medium = medium urgency OR affected_users >= 3; otherwise low. "
            "Category (Network, Hardware, Software, Other) does not change "
            "priority; it is only used for search and reports. The order "
            "matters: a high-urgency ticket with 10 users must be critical, "
            "not just high."
        ),
        "workflow_rules": (
            "Allowed moves: open -> in_progress -> resolved -> open (reopen). "
            "in_progress may also go back to open. An unassigned open ticket "
            "cannot move to in_progress; assign it first. A resolved ticket "
            "cannot jump straight to in_progress; it must be reopened first. "
            "A resolved ticket also cannot be reassigned or receive notes "
            "until it is reopened. A rejected action raises an error and "
            "leaves the ticket unchanged."
        ),
        "search_rules": (
            "Search is read-only: it returns a new list and never edits "
            "tickets. The keyword is trimmed and matched case-insensitively "
            "as a substring against the ticket title and every note message. "
            "A blank or None keyword means no keyword filter, so all tickets "
            "are returned. Optional category, status and priority filters "
            "are combined with logical AND: a ticket must match every filter "
            "that was supplied. No match returns an empty list."
        ),
        "storage_safety": (
            "On load, the whole file is parsed and validated BEFORE it "
            "replaces anything in memory. Corrupt JSON, malformed records "
            "and duplicate ticket IDs are rejected with a clear error, and "
            "the tickets already in memory stay exactly as they were. "
            "Because validation happens first, a bad file can never leave "
            "memory half-overwritten. After a successful reload, new ticket "
            "and note IDs continue from the existing ones so they cannot "
            "collide."
        ),
    }


# --- Question bank: data only, no scoring logic ---------------------------

QUESTION_BANK = [
    {
        "id": "Q1",
        "question": "Ticket T001 is open and unassigned. A user tries to move it to in_progress.",
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "answer": "B",
    },
    {
        "id": "Q2",
        "question": "The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
    },
    {
        "id": "Q3",
        "question": "Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "answer": "B",
    },
    {
        "id": "Q4",
        "question": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "answer": "C",
    },
    {
        "id": "Q5",
        "question": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "answer": "C",
    },
    {
        "id": "Q6",
        "question": "A PR changes validation but has no negative-case tests. Best review action?",
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
    },
]


# --- Scoring logic: no printing, no input ---------------------------------

def normalize_choice(raw):
    """Return 'A'-'D' for valid input (any case, trimmed), else None."""
    if not isinstance(raw, str):
        return None
    choice = raw.strip().upper()
    return choice if choice in VALID_CHOICES else None


def score_answers(answers, bank=None):
    """Score a list of submitted letters against the bank. One point each.

    `answers` holds the learner's FIRST submitted choice per question, in
    bank order. Missing or invalid entries score 0. Returns an int 0-len(bank).
    """
    bank = QUESTION_BANK if bank is None else bank
    score = 0
    for question, given in zip(bank, answers):
        if normalize_choice(given) == question["answer"]:
            score += 1
    return score


# --- Menu loop: input/output only -----------------------------------------

def ask_question(question, input_fn=input, print_fn=print):
    """Show one question; re-prompt until the input is A/B/C/D."""
    print_fn(f"\n{question['id']}. {question['question']}")
    for letter in VALID_CHOICES:
        print_fn(f"  {letter}) {question['options'][letter]}")
    while True:
        choice = normalize_choice(input_fn("Your answer (A/B/C/D): "))
        if choice:
            return choice
        print_fn("Invalid choice. Please enter A, B, C or D.")


def run_quiz(input_fn=input, print_fn=print, bank=None, explain_count=2):
    """Run the interactive quiz and return a result dict.

    Feedback is shown AFTER the first choice is recorded, so it can never
    change the score. Explanations are collected for `explain_count`
    questions and returned for mentor discussion; they are never auto-graded.
    """
    bank = QUESTION_BANK if bank is None else bank
    print_fn("=== ENGINEERING UNDERSTANDING CHECK ===")
    answers = []
    for question in bank:
        choice = ask_question(question, input_fn, print_fn)
        answers.append(choice)
        if choice == question["answer"]:
            print_fn("Recorded. Correct.")
        else:
            print_fn(f"Recorded. Not quite - the best answer was {question['answer']}.")

    score = score_answers(answers, bank)
    print_fn(f"\nFinal score: {score}/{len(bank)}")

    explanations = []
    print_fn("\nPlease explain two of your answers (for mentor discussion).")
    for question, choice in list(zip(bank, answers))[:explain_count]:
        text = ""
        while not text.strip():
            text = input_fn(f"Why did you choose {choice} for {question['id']}? ")
            if not text.strip():
                print_fn("Please write a short explanation.")
        explanations.append(
            {"question": question["id"], "choice": choice, "explanation": text.strip()}
        )

    return {"answers": answers, "score": score, "total": len(bank), "explanations": explanations}
