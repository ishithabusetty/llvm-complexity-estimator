#!/usr/bin/env python3
import subprocess, json, os, time

PLUGIN   = os.path.expanduser("~/llvm-complexity-estimator/pass/build/libComplexityPass.so")
TRAINING = os.path.expanduser("~/llvm-complexity-estimator/training")
MODEL    = os.path.expanduser("~/llvm-complexity-estimator/model/model_weights.json")

with open(MODEL) as f:
    w = json.load(f)

coef      = w["coefficients"]
intercept = w["intercept"]
mean_     = w["scaler_mean"]
std_      = w["scaler_std"]
t_cheap   = w["threshold_cheap"]
t_exp     = w["threshold_expensive"]

def predict(vals):
    scaled = [(v - m) / s for v, m, s in zip(vals, mean_, std_)]
    pred   = sum(c * x for c, x in zip(coef, scaled)) + intercept
    return max(1.0, round(pred, 1))

def verdict(pred):
    if pred < t_cheap: return "CHEAP     → full O2"
    if pred > t_exp:   return "EXPENSIVE → skip heavy passes"
    return "MEDIUM    → O1"

def time_opt(flag, llfile):
    t1 = time.time()
    subprocess.run(["opt", flag, "-disable-output", llfile], stderr=subprocess.DEVNULL)
    return round((time.time() - t1) * 1000)

print("=" * 52)
print("  LLVM IR Complexity Estimator — Demo v2.0")
print("=" * 52)
print(f"\n  Thresholds: CHEAP<{t_cheap:.0f}ms  MEDIUM={t_cheap:.0f}-{t_exp:.0f}ms  EXPENSIVE>{t_exp:.0f}ms\n")

for sample in ["sample1", "sample2", "sample3", "sample4"]:
    llfile = os.path.join(TRAINING, f"{sample}.ll")
    if not os.path.exists(llfile):
        continue

    print(f"--- {sample} ---")

    result = subprocess.run(
        ["opt", f"--load-pass-plugin={PLUGIN}",
         "-passes=complexity-pass", "-disable-output", llfile],
        stderr=subprocess.PIPE, text=True
    )

    rows = [r.strip() for r in result.stderr.strip().splitlines() if r.strip()]
    if not rows:
        print("  (no output from pass)\n")
        continue

    for row in rows:
        parts = row.split(",")
        if len(parts) < 8:
            continue
        name = parts[0]
        vals = [float(x) for x in parts[1:8]]
        pred = predict(vals)
        v    = verdict(pred)
        ic, bb, ld, phi, mem, tc, cc = [int(x) for x in vals]
        print(f"  {name:<22}  instr={ic:<4} loops={ld}  phi={phi:<2}  typeComplexity={tc:<3}  predicted={pred}ms  {v}")

    o2 = time_opt("-O2", llfile)
    o1 = time_opt("-O1", llfile)
    print(f"\n  O2={o2}ms   O1={o1}ms   saved={o2-o1}ms\n")

print("=" * 52)
print("  CHEAP → O2  |  MEDIUM → O1  |  EXPENSIVE → skip heavy")
print("=" * 52)
