# Math Adventures — ML-powered Adaptive Learning Prototype

## Overview
This is a minimal prototype that adapts math puzzle difficulty based on learner performance using a lightweight ML model (Decision Tree). It's intended for ages 5–10 to practice basic arithmetic.

## Structure
math-adaptive-prototype/
├─ README.md
├─ requirements.txt
└─ src/
├─ main.py
├─ puzzle_generator.py
├─ tracker.py
└─ adaptive_engine.py



## How it works (brief)
- `puzzle_generator.py`: produces math problems tuned to difficulty levels.
- `tracker.py`: logs attempts, correctness, response times, streaks.
- `adaptive_engine.py`: collects features from tracker, initially uses a heuristic, and retrains a DecisionTreeClassifier once enough examples are collected.
- `main.py`: command-line session runner.

## Run locally
1. create venv & install:
```bash
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
