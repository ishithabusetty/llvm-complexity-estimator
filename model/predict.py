#!/usr/bin/env python3
"""
predict.py — Ridge regression model for LLVM IR compile-time prediction.
Features: instrCount, basicBlocks, loopDepth, phiNodes, memOps, typeComplexity
Label:    compileTime_ms (instruction-weighted per-function timing)
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH     = os.path.join(BASE, "features_timed.csv")
WEIGHTS_PATH = os.path.join(BASE, "model", "model_weights.json")

FEATURES = ["instrCount", "basicBlocks", "loopDepth",
            "phiNodes", "memOps", "typeComplexity"]
TARGET   = "compileTime_ms"

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv(CSV_PATH)
print("=== Dataset ===")
print(df.to_string(index=False))
print()

if len(df) < 3:
    print("ERROR: Need at least 3 training samples. Run measure_time.sh first.")
    exit(1)

X = df[FEATURES].values.astype(float)
y = df[TARGET].values.astype(float)

# ── Scale features ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Train full model ───────────────────────────────────────────────────────────
model = Ridge(alpha=1.0)
model.fit(X_scaled, y)

# ── Leave-One-Out cross-validation ────────────────────────────────────────────
loo = LeaveOneOut()
y_pred_loo = np.zeros_like(y)
for train_idx, test_idx in loo.split(X_scaled):
    m = Ridge(alpha=1.0)
    m.fit(X_scaled[train_idx], y[train_idx])
    raw = m.predict(X_scaled[test_idx])[0]
    y_pred_loo[test_idx] = max(raw, 0.5)   # clamp: time can't be negative

mae_loo = mean_absolute_error(y, y_pred_loo)
r2_loo  = r2_score(y, y_pred_loo)

print("=== Model Evaluation (Leave-One-Out CV) ===")
for fn, actual, pred in zip(df["function"], y, y_pred_loo):
    print(f"  {fn:<18} actual={actual:5.1f}ms  predicted={pred:5.1f}ms")
print(f"\n  MAE:      {mae_loo:.2f} ms")
print(f"  R² Score: {r2_loo:.4f}")
print()

# ── Feature weights ────────────────────────────────────────────────────────────
print("=== Feature Weights ===")
for name, coef in zip(FEATURES, model.coef_):
    bar = "█" * int(abs(coef) * 5)
    sign = "+" if coef >= 0 else "-"
    print(f"  {name:<18} {sign}{abs(coef):.4f}  {bar}")
print(f"  {'intercept':<18} {model.intercept_:+.4f}")
print()

# ── Decision threshold ─────────────────────────────────────────────────────────
threshold_ms = float(np.percentile(y, 60))   # top 40% = expensive
print(f"  Decision threshold: {threshold_ms:.1f} ms  (60th percentile of training data)")
print()

# ── Predict helper (clamps to >= 0.5) ─────────────────────────────────────────
def predict_one(features_dict):
    row = np.array([[features_dict[f] for f in FEATURES]], dtype=float)
    row_scaled = scaler.transform(row)
    raw = model.predict(row_scaled)[0]
    return max(raw, 0.5)

# ── Unseen synthetic functions ─────────────────────────────────────────────────
unseen = [
    {"instrCount": 10,  "basicBlocks": 2,  "loopDepth": 0, "phiNodes": 0,
     "memOps": 4,  "typeComplexity": 5,  "label": "tiny add-like function"},
    {"instrCount": 200, "basicBlocks": 20, "loopDepth": 3, "phiNodes": 8,
     "memOps": 90, "typeComplexity": 30, "label": "deeply nested complex function"},
    {"instrCount": 45,  "basicBlocks": 8,  "loopDepth": 1, "phiNodes": 2,
     "memOps": 20, "typeComplexity": 12, "label": "medium loop function"},
]

print("=== Predicting Unseen Functions ===")
for i, fn in enumerate(unseen):
    pred = predict_one(fn)
    decision = "EXPENSIVE — skip heavy passes" if pred >= threshold_ms else "CHEAP  — run full O2"
    print(f"  Function {i+1} ({fn['label']})")
    print(f"    Features: instrs={fn['instrCount']}, BBs={fn['basicBlocks']}, "
          f"loops={fn['loopDepth']}, mem={fn['memOps']}, types={fn['typeComplexity']}")
    print(f"    Predicted: {pred:.1f}ms → {decision}")
    print()

# ── Per-function summary ───────────────────────────────────────────────────────
preds_train = np.array([max(p, 0.5) for p in model.predict(X_scaled)])
print("=== Per-Function Decisions (Training Data) ===")
print(f"  {'Function':<18} {'Actual':>8} {'Predicted':>10} {'Decision'}")
print(f"  {'-'*18} {'-'*8} {'-'*10} {'-'*25}")
correct = 0
for fn, actual, pred in zip(df["function"], y, preds_train):
    decision    = "EXPENSIVE" if pred >= threshold_ms else "CHEAP"
    act_label   = "EXPENSIVE" if actual >= threshold_ms else "CHEAP"
    marker      = "✓" if decision == act_label else "✗"
    correct    += (decision == act_label)
    print(f"  {fn:<18} {actual:>8.1f} {pred:>10.1f} {decision} {marker}")

accuracy = 100.0 * correct / len(df)
print(f"\n  Classification accuracy: {correct}/{len(df)} = {accuracy:.0f}%")
print()

# ── Save weights ───────────────────────────────────────────────────────────────
weights = {
    "features":      FEATURES,
    "coefficients":  list(model.coef_),
    "intercept":     float(model.intercept_),
    "scaler_mean":   list(scaler.mean_),
    "scaler_scale":  list(scaler.scale_),
    "threshold_ms":  threshold_ms,
    "mae_loo_ms":    mae_loo,
    "r2_loo":        r2_loo,
}
with open(WEIGHTS_PATH, "w") as f:
    json.dump(weights, f, indent=2)
print(f"Model weights saved to {WEIGHTS_PATH}")
