"""Reproducible training entry point; expects a CSV with vital columns and risk."""
import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def train(input_path: Path, output_path: Path) -> None:
    frame = pd.read_csv(input_path)
    columns = ["heart_rate", "spo2", "temperature"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(frame[columns], frame["risk"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": columns}, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    train(args.input, args.output)
