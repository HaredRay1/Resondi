"""Classification metrics. Accuracy alone is misleading here: Healthy is about half of all cycles."""
import numpy as np


def confusion(y_true, y_pred, k):
    m = np.zeros((k, k), dtype=int)
    for t, p in zip(y_true, y_pred):
        m[t, p] += 1
    return m


def report(y_true, y_pred, labels):
    k = len(labels)
    m = confusion(y_true, y_pred, k)
    n = m.sum()
    per = []
    for i, l in enumerate(labels):
        tp, fn, fp = m[i, i], m[i].sum() - m[i, i], m[:, i].sum() - m[i, i]
        tn = n - tp - fn - fp
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        spec = tn / (tn + fp) if tn + fp else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per.append({"label": l, "support": int(m[i].sum()), "precision": prec, "recall": rec,
                    "specificity": spec, "f1": f1})
    majority = m.sum(axis=1).max() / n if n else 0.0
    return {
        "n": int(n),
        "accuracy": float(np.trace(m) / n) if n else 0.0,
        "balanced_accuracy": float(np.mean([p["recall"] for p in per])),
        "macro_f1": float(np.mean([p["f1"] for p in per])),
        "majority_class_baseline": float(majority),
        "per_class": per,
        "confusion_matrix": m.tolist(),
        "confusion_rows_are": "true label",
    }


def to_text(r, labels, title):
    lines = [title, "=" * len(title),
             f"items: {r['n']}",
             f"accuracy: {r['accuracy']:.3f}   (always guessing the commonest class scores {r['majority_class_baseline']:.3f})",
             f"balanced accuracy: {r['balanced_accuracy']:.3f}   macro F1: {r['macro_f1']:.3f}", "",
             f"{'class':<24}{'support':>8}{'precision':>11}{'recall':>8}{'specif.':>9}{'F1':>7}"]
    for p in r["per_class"]:
        lines.append(f"{p['label']:<24}{p['support']:>8}{p['precision']:>11.3f}{p['recall']:>8.3f}"
                     f"{p['specificity']:>9.3f}{p['f1']:>7.3f}")
    lines += ["", "confusion matrix (rows = true, columns = predicted)",
              " " * 24 + "".join(f"{l[:10]:>12}" for l in labels)]
    for l, row in zip(labels, r["confusion_matrix"]):
        lines.append(f"{l:<24}" + "".join(f"{v:>12}" for v in row))
    return "\n".join(lines)
