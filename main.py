# src/main.py
import time
import argparse
from puzzle_generator import generate_puzzle, OPERATIONS
from tracker import Tracker
from adaptive_engine import MLAdaptiveEngine, INT_TO_DIFF, DIFF_TO_INT
import math

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=20, help="Number of puzzles in session")
    return p.parse_args()

def get_user_input(prompt:str):
    try:
        return input(prompt)
    except EOFError:
        return ''

def main():
    args = parse_args()
    print("=== Math Adventures (ML-based adaptive prototype) ===")
    name = get_user_input("Enter learner name: ").strip() or "Learner"
    print(f"Welcome, {name}!")

    # choose initial difficulty
    diffs = ["easy", "medium", "hard"]
    chosen = ''
    while chosen not in diffs:
        chosen = get_user_input("Choose starting difficulty (easy / medium / hard): ").strip().lower()
        if chosen == '':
            chosen = 'easy'
            break
    cur_diff = DIFF_TO_INT[chosen]

    # optionally let user pick operation or random
    op_choice = get_user_input("Pick operation (+ - * /) or press Enter for mixed: ").strip()
    if op_choice not in OPERATIONS:
        op_choice = None

    tracker = Tracker()
    engine = MLAdaptiveEngine(min_samples_for_training=12, history_window=6)
    engine.last_difficulty = cur_diff

    total_rounds = args.rounds
    print(f"Starting session: {total_rounds} rounds. Operation: {op_choice or 'mixed'}")

    for r in range(total_rounds):
        # generate
        q, correct_ans = generate_puzzle(engine.last_difficulty, operation=op_choice)
        print(f"\nRound {r+1}/{total_rounds} | Difficulty: {INT_TO_DIFF[engine.last_difficulty].upper()}")
        print("Solve:", q)
        start = time.time()
        raw = get_user_input("Your answer: ").strip()
        elapsed = time.time() - start
        # simple parsing
        try:
            user_ans = float(raw)
        except:
            user_ans = float('nan')

        # check correctness: for division or floats allow small tolerance
        tol = 0.01
        correct = False
        if math.isfinite(user_ans):
            correct = abs(user_ans - correct_ans) <= tol
        else:
            correct = False

        if correct:
            print(f"Correct! (Answer: {correct_ans})")
        else:
            print(f"Incorrect. Correct answer: {correct_ans}")

        # log attempt
        # deduce operation from question string (split)
        operation = q.split()[1] if len(q.split())>=3 else '?'
        tracker.log_attempt(q, correct_ans, user_ans, correct, elapsed, engine.last_difficulty, operation)

        # Decide next difficulty (predict)
        next_diff = engine.predict_next(tracker)

        # Add training example: mapping current features -> chosen next difficulty
        engine.add_training_example(tracker, next_diff)

        print(f"Next difficulty set to: {INT_TO_DIFF[next_diff].upper()}")
        if r % 5 == 4:
            print(engine.explain_last())

    # session summary
    s = tracker.summary()
    print("\n=== Session Summary ===")
    print(f"Rounds: {s['total']}")
    print(f"Correct: {s['correct']}")
    print(f"Accuracy: {s['accuracy']*100:.1f}%")
    print(f"Average response time: {s['avg_time']:.2f}s")
    print(f"Current streak: {s['streak']}")
    print(f"Recommended next level: {INT_TO_DIFF[engine.last_difficulty].upper()}")
    print("Thanks for playing!")

if __name__ == "__main__":
    main()






## How it works (brief)
"""- `puzzle_generator.py`: produces math problems tuned to difficulty levels.
- `tracker.py`: logs attempts, correctness, response times, streaks.
- `adaptive_engine.py`: collects features from tracker, initially uses a heuristic, and retrains a DecisionTreeClassifier once  enough examples are collected.
- `main.py`: command-line session runner."""