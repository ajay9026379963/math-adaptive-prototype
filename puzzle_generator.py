# src/puzzle_generator.py
import random
import time
from typing import Tuple

# Difficulty mapping: 0=Easy, 1=Medium, 2=Hard
DIFFICULTY_RANGES = {
    0: (1, 10),
    1: (5, 20),
    2: (10, 100)
}

OPERATIONS = ['+', '-', '*', '/']

def generate_puzzle(difficulty:int, operation: str = None) -> Tuple[str, float, float]:
    """
    Return: (question_str, correct_answer (float), time_hint)
    Note: division results are rounded to 2 decimals for user's comparison.
    """
    if operation is None:
        operation = random.choice(OPERATIONS)
    lo, hi = DIFFICULTY_RANGES.get(difficulty, (1,10))

    # Make numbers more sensible for children: avoid negative results for subtraction at low levels
    if operation == '+':
        a = random.randint(lo, hi)
        b = random.randint(lo, hi)
        ans = a + b
    elif operation == '-':
        a = random.randint(lo, hi)
        b = random.randint(lo, a) if difficulty == 0 else random.randint(lo, hi)
        ans = a - b
    elif operation == '*':
        # For easy, small multipliers
        if difficulty == 0:
            a = random.randint(1, 10)
            b = random.randint(1, 10)
        elif difficulty == 1:
            a = random.randint(2, 12)
            b = random.randint(2, 12)
        else:
            a = random.randint(5, 20)
            b = random.randint(2, 12)
        ans = a * b
    elif operation == '/':
        # make divisible or give decimal to 2 dp
        if difficulty == 0:
            b = random.randint(1, 10)
            q = random.randint(1, 10)
            a = b * q
            ans = a / b
        else:
            b = random.randint(1 + lo//2, hi//2 + 1)
            q = random.randint(lo, hi)
            a = b * q
            ans = a / b
    else:
        raise ValueError("Unknown operation")

    question = f"{a} {operation} {b} = ?"
    # return answer as float for consistent checking
    return question, float(ans)
