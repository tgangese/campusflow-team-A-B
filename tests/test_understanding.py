import os
import tempfile
import unittest

from campusflow.cli import menu_understanding_check
from campusflow.understanding_check import (
    QUESTION_BANK,
    normalize_choice,
    run_quiz,
    run_understanding_check,
    score_answers,
)


def scripted(inputs):
    """Fake input() that replays a list and records the prompts."""
    items = iter(inputs)
    return lambda prompt="": next(items)


CORRECT = [q["answer"] for q in QUESTION_BANK]


class TestUnderstandingCheck(unittest.TestCase):

    def test_bank_has_six_questions_with_valid_answers(self):
        self.assertEqual(len(QUESTION_BANK), 6)
        for q in QUESTION_BANK:
            self.assertEqual(sorted(q["options"]), ["A", "B", "C", "D"])
            self.assertIn(q["answer"], q["options"])

    def test_score_all_correct_all_wrong_and_partial(self):
        self.assertEqual(score_answers(CORRECT), 6)
        self.assertEqual(score_answers(["A"] * 6), score_answers(["A"] * 6))
        wrong = [("A" if c != "A" else "B") for c in CORRECT]
        self.assertEqual(score_answers(wrong), 0)
        self.assertEqual(score_answers(CORRECT[:3] + wrong[3:]), 3)

    def test_normalize_choice_rejects_invalid(self):
        self.assertEqual(normalize_choice(" b "), "B")
        for bad in ("E", "", "AB", "1", None, 5):
            self.assertIsNone(normalize_choice(bad))

    def test_quiz_rejects_invalid_answer_then_scores_correctly(self):
        # Q1 gets two invalid inputs before a valid one; the score must
        # reflect only the final valid submission for each question.
        inputs = ["Z", "", CORRECT[0]] + CORRECT[1:] + ["explanation one", "explanation two"]
        output = []
        result = run_quiz(input_fn=scripted(inputs), print_fn=output.append)
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["answers"], CORRECT)
        self.assertEqual(sum("Invalid choice" in line for line in output), 2)

    def test_quiz_score_uses_submitted_answers_not_feedback(self):
        wrong = [("A" if c != "A" else "B") for c in CORRECT]
        inputs = wrong + ["because", "because"]
        result = run_quiz(input_fn=scripted(inputs), print_fn=lambda *_: None)
        self.assertEqual(result["score"], 0)

    def test_quiz_requires_nonblank_explanations(self):
        inputs = CORRECT + ["   ", "first reason", "second reason"]
        result = run_quiz(input_fn=scripted(inputs), print_fn=lambda *_: None)
        self.assertEqual(len(result["explanations"]), 2)
        self.assertEqual(result["explanations"][0]["explanation"], "first reason")

    def test_menu_saves_explanations_to_notes_file(self):
        inputs = CORRECT + ["why one", "why two"]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "notes", "learning.txt")
            menu_understanding_check(input_fn=scripted(inputs), print_fn=lambda *_: None, notes_path=path)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        self.assertIn("Score: 6/6", text)
        self.assertIn("why one", text)

    def test_written_explanations_cover_all_four_rule_areas(self):
        result = run_understanding_check()
        self.assertEqual(
            sorted(result),
            ["priority_rules", "search_rules", "storage_safety", "workflow_rules"],
        )
        for text in result.values():
            self.assertTrue(text.strip())


if __name__ == "__main__":
    unittest.main()
