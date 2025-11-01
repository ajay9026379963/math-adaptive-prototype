# src/tracker.py
import time
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Attempt:
    question: str
    correct_answer: float
    user_answer: float
    correct: bool
    response_time: float
    difficulty: int
    operation: str

@dataclass
class Tracker:
    attempts: List[Attempt] = field(default_factory=list)

    def log_attempt(self, question:str, correct_answer:float, user_answer:float,
                    correct:bool, response_time:float, difficulty:int, operation:str):
        att = Attempt(question, correct_answer, user_answer, correct, response_time, difficulty, operation)
        self.attempts.append(att)

    def accuracy_last_n(self, n:int):
        last = self.attempts[-n:] if len(self.attempts) >= 1 else []
        if not last:
            return 0.0
        return sum(1 for a in last if a.correct) / len(last)

    def avg_time_last_n(self, n:int):
        last = self.attempts[-n:] if len(self.attempts) >= 1 else []
        if not last:
            return 0.0
        return sum(a.response_time for a in last) / len(last)

    def current_streak(self):
        # count recent consecutive correct answers
        streak = 0
        for a in reversed(self.attempts):
            if a.correct:
                streak += 1
            else:
                break
        return streak

    def summary(self) -> Dict:
        total = len(self.attempts)
        correct = sum(1 for a in self.attempts if a.correct)
        avg_time = sum(a.response_time for a in self.attempts)/total if total>0 else 0.0
        return {
            "total": total,
            "correct": correct,
            "accuracy": correct/total if total>0 else 0.0,
            "avg_time": avg_time,
            "streak": self.current_streak()
        }
