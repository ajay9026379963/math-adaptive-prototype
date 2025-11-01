# src/adaptive_engine.py
from typing import List, Dict
from collections import deque
import numpy as np

# Lightweight ML
from sklearn.tree import DecisionTreeClassifier

# mapping difficulties to ints
DIFF_TO_INT = {"easy":0, "medium":1, "hard":2}
INT_TO_DIFF = {v:k for k,v in DIFF_TO_INT.items()}

class MLAdaptiveEngine:
    def __init__(self, min_samples_for_training:int = 12, history_window:int = 8):
        """
        min_samples_for_training: number of (feature,label) pairs needed before
                                   training ML model
        history_window: how many last attempts to compute rolling features
        """
        self.min_samples = min_samples_for_training
        self.window = history_window
        self.dataset_X = []
        self.dataset_y = []
        self.model = None
        self.clf = DecisionTreeClassifier(max_depth=5)
        # last chosen difficulty (int)
        self.last_difficulty = DIFF_TO_INT["easy"]

    def features_from_tracker(self, tracker) -> List[float]:
        # compute features: accuracy_last_w, avg_time_last_w, streak, last_correct, current_difficulty
        w = self.window
        acc = tracker.accuracy_last_n(w)
        avg_t = tracker.avg_time_last_n(w)
        streak = tracker.current_streak()
        last_correct = 1 if (len(tracker.attempts)>0 and tracker.attempts[-1].correct) else 0
        cur_diff = self.last_difficulty
        # normalize times to a rough scale: clamp
        avg_t_clamped = min(avg_t, 30.0)  # seconds cap
        return [acc, avg_t_clamped, streak, last_correct, cur_diff]

    def heuristic_decision(self, features) -> int:
        # features: [acc, avg_t, streak, last_correct, cur_diff]
        acc, avg_t, streak, last_correct, cur_diff = features
        # simple heuristic thresholds
        if acc >= 0.8 and (avg_t <= 8 or streak >= 3):
            return min(2, cur_diff + 1)  # increase difficulty
        elif acc < 0.5 or last_correct == 0 and streak==0:
            return max(0, cur_diff - 1)  # decrease
        else:
            return cur_diff  # stay

    def predict_next(self, tracker):
        feats = self.features_from_tracker(tracker)
        # if not enough data, fall back to heuristic
        if len(self.dataset_y) < self.min_samples:
            next_d = self.heuristic_decision(feats)
            # do not train on heuristic for now; we'll add (features->next_d) when we choose to log
        else:
            X = np.array([feats])
            y_pred = self.clf.predict(X)
            next_d = int(y_pred[0])
        # update last difficulty
        self.last_difficulty = next_d
        return next_d

    def add_training_example(self, tracker, next_d:int):
        feats = self.features_from_tracker(tracker)
        self.dataset_X.append(feats)
        self.dataset_y.append(next_d)
        # if enough samples, train model
        if len(self.dataset_y) >= self.min_samples:
            self.train_model()

    def train_model(self):
        import numpy as np
        X = np.array(self.dataset_X)
        y = np.array(self.dataset_y)
        self.clf.fit(X, y)
        self.model = self.clf  # reference

    def explain_last(self):
        if self.model is None:
            return "Using heuristic (not enough data)."
        return "Using trained DecisionTreeClassifier."
