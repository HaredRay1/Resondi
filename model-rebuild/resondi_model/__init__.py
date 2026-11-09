"""Resondi lung sound classifier: data preparation, features, model, metrics."""
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def load_config(path=None):
    with open(path or os.path.join(ROOT, "config", "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["labels"] == sorted(cfg["labels"]), "labels must stay in alphabetical order (Edge Impulse output order)"
    assert len(cfg["labels"]) == 4
    return cfg
