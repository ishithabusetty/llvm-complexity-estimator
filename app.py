import streamlit as st
import json
import os
import re
import subprocess
import tempfile
import time
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="LLVM IR Complexity Estimator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Ground-truth training data (exact values from your terminal output) ────────
TRAINING_DATA = [
    {"fn": "add",             "file": "sample1", "instrs": 8,  "bbs": 1,  "loops": 0, "phi": 0, "mem": 4,  "types": 3, "actual": 1.0,  "pred": 1.2},
    {"fn": "sumArray",        "file": "sample1", "instrs": 28, "bbs": 5,  "loops": 1, "phi": 0, "mem": 14, "types": 6, "actual": 4.0,  "pred": 3.0},
    {"fn": "matMul",          "file": "sample1", "instrs": 75, "bbs": 13, "loops": 3, "phi": 0, "mem": 32, "types": 6, "actual": 11.0, "pred": 6.8},
    {"fn": "fibonacci",       "file": "sample2", "instrs": 39, "bbs": 8,  "loops": 1, "phi": 0, "mem": 21, "types": 5, "actual": 6.0,  "pred": 3.9},
    {"fn": "copyArray",       "file": "sample2", "instrs": 29, "bbs": 5,  "loops": 1, "phi": 0, "mem": 14, "types": 6, "actual": 4.0,  "pred": 3.1},
    {"fn": "classify",        "file": "sample2", "instrs": 27, "bbs": 10, "loops": 0, "phi": 0, "mem": 11, "types": 5, "actual": 4.0,  "pred": 2.7},
    {"fn": "dot",             "file": "sample3", "instrs": 30, "bbs": 1,  "loops": 0, "phi": 0, "mem": 10, "types": 7, "actual": 3.0,  "pred": 2.3},
    {"fn": "normalize",       "file": "sample3", "instrs": 51, "bbs": 3,  "loops": 0, "phi": 0, "mem": 29, "types": 6, "actual": 4.0,  "pred": 4.1},
    {"fn": "transformPoints", "file": "sample3", "instrs": 51, "bbs": 5,  "loops": 1, "phi": 0, "mem": 25, "types": 7, "actual": 4.0,  "pred": 4.4},
    {"fn": "searchMatrix",    "file": "sample3", "instrs": 51, "bbs": 12, "loops": 2, "phi": 0, "mem": 22, "types": 6, "actual": 4.0,  "pred": 5.0},
    {"fn": "gcd",             "file": "sample4", "instrs": 20, "bbs": 4,  "loops": 1, "phi": 0, "mem": 11, "types": 5, "actual": 1.0,  "pred": 2.5},
    {"fn": "isPrime",         "file": "sample4", "instrs": 33, "bbs": 10, "loops": 1, "phi": 0, "mem": 14, "types": 5, "actual": 2.0,  "pred": 3.5},
    {"fn": "bubbleSort",      "file": "sample4", "instrs": 72, "bbs": 11, "loops": 2, "phi": 0, "mem": 33, "types": 6, "actual": 5.0,  "pred": 6.3},
    {"fn": "binarySearch",    "file": "sample4", "instrs": 58, "bbs": 10, "loops": 1, "phi": 0, "mem": 28, "types": 6, "actual": 4.0,  "pred": 5.1},
    {"fn": "prefixSum",       "file": "sample4", "instrs": 42, "bbs": 5,  "loops": 1, "phi": 0, "mem": 21, "types": 6, "actual": 3.0,  "pred": 3.9},
    {"fn": "deepNest",        "file": "sample5", "instrs": 56, "bbs": 13, "loops": 3, "phi": 0, "mem": 23, "types": 6, "actual": 5.0,  "pred": 5.7},
    {"fn": "tensorOp",        "file": "sample5", "instrs": 74, "bbs": 13, "loops": 3, "phi": 0, "mem": 30, "types": 7, "actual": 6.0,  "pred": 6.7},
    {"fn": "maxIn3D",         "file": "sample5", "instrs": 71, "bbs": 15, "loops": 3, "phi": 0, "mem": 29, "types": 6, "actual": 6.0,  "pred": 6.8},
]

WEIGHTS = {"instrCount": 0.7459, "basicBlocks": 0.2185, "loopDepth": 0.4043,
           "phiNodes": 0.0000, "memOps": 0.3900, "typeComplexity": -0.0075,
           "intercept": 4.2778}
SCALER_MEAN  = [43.2, 8.2, 1.3, 0.0, 21.0, 6.1]
SCALER_SCALE = [19.5, 4.1, 1.1, 0.01, 8.3, 0.8]
THRESHOLD    = 4.0
FEATURE_KEYS = ["instrCount", "basicBlocks", "loopDepth", "phiNodes", "memOps", "typeComplexity"]

LOO_RESULTS = {d["fn"]: d["pred"] for d in TRAINING_DATA}
LOO_ACTUAL  = {d["fn"]: d["actual"] for d in TRAINING_DATA}

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Helpers ───────────────────────────────────────────────────────────────────
def predict_ms(features: dict) -> float:
    vals = [features[k] for k in FEATURE_KEYS]
    score = WEIGHTS["intercept"]
    for i, k in enumerate(FEATURE_KEYS):
        score += WEIGHTS[k] * (vals[i] - SCALER_MEAN[i]) / SCALER_SCALE[i]
    return max(score, 0.5)

def estimate_features(code: str) -> dict:
    lines = code.split("\n")
    instrs = 0; bbs = 1; depth = 0; max_depth = 0; mem = 0; types = 3.0
    for line in lines:
        t = line.strip()
        if not t or t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        if re.search(r'\bfor\b|\bwhile\b|\bdo\b', t):
            depth += 1
            max_depth = max(max_depth, depth)
        if re.search(r'^\s*\}', t):
            depth = max(0, depth - 1)
        if re.search(r'\bif\b|\belse\b|\bfor\b|\bwhile\b|\bswitch\b|\bcase\b', t):
            bbs += 1
        instrs += len(re.findall(r'[;,]', t))
        if re.search(r'\b\w+\s*=\s*[^=]', t):
            instrs += 1
        if re.search(r'\w+\[', t):
            mem += 1; instrs += 1
        if re.search(r'->|\*\w', t):
            mem += 1; instrs += 1
        type_hits = len(re.findall(r'\bint\b|\bfloat\b|\bdouble\b|\bchar\b|\bvoid\b|\blong\b', t))
        types = min(types + type_hits * 0.5, 12)
    instrs = max(instrs, 5)
    mem    = max(mem, int(instrs * 0.35))
    return {"instrCount": int(instrs), "basicBlocks": int(bbs),
            "loopDepth": max_depth, "phiNodes": 0,
            "memOps": int(mem), "typeComplexity": round(types)}

def parse_functions(code: str):
    pattern = re.compile(r'(\w[\w\s\*]*?)\s+(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    skip = {'if','for','while','switch','else','do'}
    fns = []
    for m in pattern.finditer(code):
        name = m.group(2)
        if name in skip:
            continue
        start = m.start()
        depth = 0
        for i in range(start, len(code)):
            if code[i] == '{': depth += 1
            elif code[i] == '}':
                depth -= 1
                if depth == 0:
                    fns.append({"name": name, "body": code[start:i+1]})
                    break
    return fns if fns else [{"name": "(function)", "body": code}]

def try_llvm_analysis(code: str):
    """Try to use real LLVM pass if available, return None if not."""
    pass_so = Path.home() / "llvm-complexity-estimator/pass/build/libComplexityPass.so"
    if not pass_so.exists():
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            c_file = os.path.join(tmp, "input.c")
            ll_file = os.path.join(tmp, "input.ll")
            with open(c_file, "w") as f:
                f.write(code)
            r1 = subprocess.run(
                ["clang", "-O0", "-emit-llvm", "-S", c_file, "-o", ll_file],
                capture_output=True, timeout=10)
            if r1.returncode != 0:
                return None
            r2 = subprocess.run(
                ["opt", f"--load-pass-plugin={pass_so}",
                 "-passes=complexity-pass", "-disable-output", ll_file],
                capture_output=True, text=True, timeout=10)
            rows = []
            for line in r2.stderr.strip().splitlines():
                parts = line.strip().split(",")
                if len(parts) == 7:
                    rows.append({
                        "name": parts[0],
                        "features": {
                            "instrCount": int(parts[1]), "basicBlocks": int(parts[2]),
                            "loopDepth": int(parts[3]), "phiNodes": int(parts[4]),
                            "memOps": int(parts[5]), "typeComplexity": int(parts[6]),
                        }
                    })
            return rows if rows else None
    except Exception:
        return None

def analyse_code(code: str, label: str):
    llvm_rows = try_llvm_analysis(code)
    using_llvm = llvm_rows is not None
    if using_llvm:
        parsed = llvm_rows
    else:
        fns = parse_functions(code)
        parsed = [{"name": fn["name"], "features": estimate_features(fn["body"])} for fn in fns]

    results = []
    for item in parsed:
        pred = predict_ms(item["features"])
        results.append({**item, "pred": round(pred, 1),
                        "decision": "EXPENSIVE" if pred >= THRESHOLD else "CHEAP"})
    entry = {
        "label": label,
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M:%S"),
        "functions": results,
        "using_llvm": using_llvm,
        "code": code,
    }
    st.session_state.history.insert(0, entry)
    return entry

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-row{display:flex;gap:12px;margin-bottom:1rem}
.metric-box{flex:1;background:#f8f8fb;border-radius:8px;padding:12px 16px;border:1px solid #ebebf0}
.metric-lbl{font-size:11px;color:#888;margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.metric-val{font-size:24px;font-weight:600;color:#222}
.metric-sub{font-size:11px;color:#aaa;margin-top:2px}
.fn-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #f0f0f0}
.fn-row:last-child{border-bottom:none}
.fn-name{font-weight:600;font-size:13px;min-width:130px}
.badge-cheap{background:#eaf3de;color:#3B6D11;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600}
.badge-exp{background:#faece7;color:#993C1D;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600}
.bar-wrap{flex:1;height:6px;background:#ebebf0;border-radius:3px;overflow:hidden}
.bar-fill-purple{height:100%;background:#7F77DD;border-radius:3px}
.bar-fill-red{height:100%;background:#D85A30;border-radius:3px}
.decision-box{padding:12px 16px;border-radius:8px;margin-top:12px;font-size:13px}
.decision-cheap{background:#eaf3de;border-left:4px solid #3B6D11;color:#3B6D11}
.decision-exp{background:#faece7;border-left:4px solid #993C1D;color:#993C1D}
.llvm-badge{background:#e6f1fb;color:#185FA5;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.est-badge{background:#faeeda;color:#854F0B;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.section-head{font-size:15px;font-weight:600;margin-bottom:8px;color:#222}
.tick{color:#3B6D11;font-weight:700}
.cross{color:#993C1D;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ LLVM Estimator")
    st.caption("Complexity & compile-time prediction")
    st.divider()
    page = st.radio("Navigation", ["Analyze code", "Deliverables", "Model & weights", "History"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown("**History**")
    if not st.session_state.history:
        st.caption("No analyses yet")
    else:
        for i, h in enumerate(st.session_state.history):
            n_exp = sum(1 for f in h["functions"] if f["decision"] == "EXPENSIVE")
            icon = "🔴" if n_exp else "🟢"
            if st.button(f"{icon} {h['label']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.selected_history = i
                page = "History"
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.pop("selected_history", None)
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Analyze
# ══════════════════════════════════════════════════════════════════════════════
if page == "Analyze code":
    st.markdown("## Analyze a C function")
    st.caption("Upload a `.c` file or paste code — features are extracted and compile-time predicted using the trained model.")

    tab_paste, tab_upload = st.tabs(["Paste code", "Upload .c file"])

    with tab_paste:
        label_paste = st.text_input("Label / filename", value="myfile.c", key="label_paste")
        code_paste = st.text_area("C code", height=220, key="code_paste",
            placeholder="int bubbleSort(int *arr, int n) {\n    for (int i=0;i<n-1;i++)\n        for (int j=0;j<n-i-1;j++)\n            if (arr[j]>arr[j+1]) { int t=arr[j]; arr[j]=arr[j+1]; arr[j+1]=t; }\n    return 0;\n}")
        if st.button("Run analysis", type="primary", key="run_paste"):
            if code_paste.strip():
                with st.spinner("Extracting IR features..."):
                    entry = analyse_code(code_paste.strip(), label_paste)
                st.session_state.last_entry = entry
            else:
                st.warning("Paste some C code first.")

    with tab_upload:
        uploaded = st.file_uploader("Upload a .c file", type=["c", "h", "cpp"])
        if uploaded:
            code_up = uploaded.read().decode("utf-8", errors="replace")
            label_up = uploaded.name
            st.code(code_up[:800] + ("..." if len(code_up) > 800 else ""), language="c")
            if st.button("Run analysis", type="primary", key="run_upload"):
                with st.spinner("Extracting IR features..."):
                    entry = analyse_code(code_up, label_up)
                st.session_state.last_entry = entry

    entry = st.session_state.get("last_entry")
    if entry:
        st.divider()
        mode_html = (
            '<span class="llvm-badge">LLVM pass (exact)</span>'
            if entry["using_llvm"] else
            '<span class="est-badge">JS estimator (approximate)</span>'
        )
        st.markdown(f"**{entry['label']}** &nbsp; {mode_html} &nbsp; `{entry['timestamp']}`",
                    unsafe_allow_html=True)

        fns = entry["functions"]
        max_instrs = max(f["features"]["instrCount"] for f in fns) or 1

        col_heads = ["Function", "Instrs", "BBs", "Loop depth", "Mem ops", "Types", "Predicted", "Decision"]
        rows = []
        for f in fns:
            ft = f["features"]
            rows.append({
                "Function": f["name"],
                "Instrs": ft["instrCount"],
                "BBs": ft["basicBlocks"],
                "Loop depth": ft["loopDepth"],
                "Mem ops": ft["memOps"],
                "Types": ft["typeComplexity"],
                "Predicted (ms)": f["pred"],
                "Decision": f["decision"],
            })
        df = pd.DataFrame(rows)

        def colour_decision(val):
            if val == "EXPENSIVE":
                return "background-color:#faece7;color:#993C1D;font-weight:600"
            return "background-color:#eaf3de;color:#3B6D11;font-weight:600"

        st.dataframe(
            df.style.map(colour_decision, subset=["Decision"]),
            use_container_width=True, hide_index=True
        )

        expensive = [f for f in fns if f["decision"] == "EXPENSIVE"]
        cheap     = [f for f in fns if f["decision"] == "CHEAP"]

        if expensive:
            st.markdown(f"""<div class="decision-box decision-exp">
            <b>Pipeline decision: EXPENSIVE — route to O1</b><br>
            Expensive: {', '.join(f['name'] for f in expensive)}<br>
            Cheap: {', '.join(f['name'] for f in cheap) or 'none'}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="decision-box decision-cheap">
            <b>Pipeline decision: CHEAP — run full O2</b><br>
            All functions below threshold ({THRESHOLD}ms). No pass skipping needed.
            </div>""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Functions analysed", len(fns))
        c2.metric("Expensive", len(expensive))
        c3.metric("Cheap", len(cheap))
        c4.metric("Peak predicted", f"{max(f['pred'] for f in fns):.1f}ms")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Deliverables
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Deliverables":
    st.markdown("## Project deliverables")
    st.caption("All 5 assignment deliverables — status, approach, and key outputs.")

    deliverables = [
        ("1", "IR feature extractor",
         "ComplexityPass.cpp runs as an LLVM 18 function pass and emits 6 features per function to stderr: instrCount, basicBlocks, loopDepth (fixed with recursive subloop walk), phiNodes, memOps, typeComplexity. Loop depth bug fixed by recursing into getSubLoops() instead of calling getLoopDepth() on top-level loops only.",
         "matMul → loopDepth=3 ✓ (was incorrectly 1 before fix)"),
        ("2", "Compile-time measurement infrastructure",
         "measure_time.sh compiles each .c to .ll via clang -O0 -emit-llvm, then times opt -O2 over 3 runs (minimum taken to reduce noise). Each function is assigned an instruction-weighted share of the file's compile time rather than an equal split.",
         "5 files × 18 functions. Weighted attribution: compileTime_fn = (instrCount_fn / totalInstrs) × fileTime_ms"),
        ("3", "Prediction model",
         "Ridge regression (α=1.0) trained on 6 features with StandardScaler normalisation. Weights serialised to model_weights.json so demo.sh can predict without retraining. Threshold at 60th percentile.",
         "instrCount=+0.75, loopDepth=+0.40, memOps=+0.39. All dominant coefficients have correct sign."),
        ("4", "Evaluation on unseen functions",
         "Leave-One-Out cross-validation on all 18 training functions. For each fold, the model is retrained on 17 samples and tested on the held-out function. Results reported below.",
         "MAE=1.50ms, R²=0.26 (LOO), Binary accuracy=78% (14/18)"),
        ("5", "Demo: pass skipping + savings",
         "demo.sh loads model_weights.json, applies StandardScaler + Ridge coefficients per function, and routes files with any EXPENSIVE function to opt -O1. Files with only CHEAP functions run full O2. Timing delta reported.",
         "4/5 files routed to O1. Timing savings small on toy files — expected, real savings appear at production scale."),
    ]

    for num, title, desc, result in deliverables:
        with st.expander(f"✅  Deliverable {num} — {title}", expanded=True):
            st.markdown(desc)
            st.info(f"**Result:** {result}")

    st.divider()
    st.markdown("### Training corpus — all 18 functions")

    df_train = pd.DataFrame(TRAINING_DATA)
    df_train = df_train.rename(columns={
        "fn": "Function", "file": "File", "instrs": "Instrs",
        "bbs": "BBs", "loops": "Loop depth", "phi": "Phi",
        "mem": "Mem ops", "types": "Types",
        "actual": "Actual (ms)", "pred": "LOO Predicted (ms)"
    })
    df_train["Decision"] = df_train["LOO Predicted (ms)"].apply(
        lambda p: "EXPENSIVE" if p >= THRESHOLD else "CHEAP")
    df_train["Actual decision"] = df_train["Actual (ms)"].apply(
        lambda a: "EXPENSIVE" if a >= THRESHOLD else "CHEAP")
    df_train["✓"] = df_train.apply(
        lambda r: "✓" if r["Decision"] == r["Actual decision"] else "✗", axis=1)

    def style_decision(val):
        if val == "EXPENSIVE": return "background-color:#faece7;color:#993C1D;font-weight:600"
        if val == "CHEAP":     return "background-color:#eaf3de;color:#3B6D11;font-weight:600"
        return ""
    def style_tick(val):
        if val == "✓": return "color:#3B6D11;font-weight:700"
        if val == "✗": return "color:#993C1D;font-weight:700"
        return ""

    display_cols = ["Function", "File", "Instrs", "Loop depth", "Mem ops",
                    "Actual (ms)", "LOO Predicted (ms)", "Decision", "✓"]
    styled = (df_train[display_cols].style
              .map(style_decision, subset=["Decision"])
              .map(style_tick, subset=["✓"]))
    st.dataframe(styled, use_container_width=True, hide_index=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MAE", "1.50 ms")
    c2.metric("R² (LOO)", "0.26")
    c3.metric("Classification accuracy", "78%")
    c4.metric("Correct predictions", "14 / 18")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Model & Weights
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Model & weights":
    st.markdown("## Model & feature weights")
    st.caption("Trained Ridge regression — exact coefficients from your predict.py output.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Feature coefficients")
        coef_data = {k: v for k, v in WEIGHTS.items() if k != "intercept"}
        df_w = pd.DataFrame({
            "Feature": list(coef_data.keys()),
            "Coefficient": list(coef_data.values()),
        })
        df_w["abs"] = df_w["Coefficient"].abs()
        df_w = df_w.sort_values("abs", ascending=True)

        import plotly.graph_objects as go
        colors = ["#D85A30" if v < 0 else "#7F77DD" for v in df_w["Coefficient"]]
        fig = go.Figure(go.Bar(
            x=df_w["Coefficient"], y=df_w["Feature"],
            orientation='h', marker_color=colors,
            text=[f"{v:+.4f}" for v in df_w["Coefficient"]],
            textposition='outside'
        ))
        fig.update_layout(
            margin=dict(l=0, r=60, t=10, b=10), height=280,
            xaxis_title="Coefficient (scaled)", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), xaxis=dict(zeroline=True, zerolinecolor="#ccc")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Intercept: +{WEIGHTS['intercept']:.4f} | Threshold: {THRESHOLD}ms | Ridge α=1.0")

    with col2:
        st.markdown("### LOO cross-validation results")
        loo_rows = []
        for d in TRAINING_DATA:
            act_dec = "EXPENSIVE" if d["actual"] >= THRESHOLD else "CHEAP"
            prd_dec = "EXPENSIVE" if d["pred"]   >= THRESHOLD else "CHEAP"
            loo_rows.append({
                "Function": d["fn"],
                "Actual (ms)": d["actual"],
                "Predicted (ms)": d["pred"],
                "Correct": "✓" if act_dec == prd_dec else "✗"
            })
        df_loo = pd.DataFrame(loo_rows)

        def style_correct(val):
            if val == "✓": return "color:#3B6D11;font-weight:700"
            return "color:#993C1D;font-weight:700"

        st.dataframe(
            df_loo.style.map(style_correct, subset=["Correct"]),
            use_container_width=True, hide_index=True, height=340
        )

    st.divider()
    st.markdown("### Unseen function predictions")
    unseen = [
        {"Description": "Tiny add-like function",       "Instrs": 10,  "BBs": 2,  "Loops": 0, "Mem": 4,  "Types": 5,  "Predicted": 1.4},
        {"Description": "Deeply nested complex function","Instrs": 200, "BBs": 20, "Loops": 3, "Mem": 90, "Types": 30, "Predicted": 14.4},
        {"Description": "Medium loop function",          "Instrs": 45,  "BBs": 8,  "Loops": 1, "Mem": 20, "Types": 12, "Predicted": 4.1},
    ]
    df_u = pd.DataFrame(unseen)
    df_u["Decision"] = df_u["Predicted"].apply(lambda p: "EXPENSIVE" if p >= THRESHOLD else "CHEAP")
    st.dataframe(
        df_u.style.map(
            lambda v: "background-color:#faece7;color:#993C1D;font-weight:600"
                      if v == "EXPENSIVE" else
                      ("background-color:#eaf3de;color:#3B6D11;font-weight:600" if v == "CHEAP" else ""),
            subset=["Decision"]
        ),
        use_container_width=True, hide_index=True
    )

    st.divider()
    st.markdown("### Demo pipeline results")
    demo = [
        {"File": "sample1.c", "Key expensive fn": "matMul (6.8ms, depth 3)", "O2 time": "15ms", "O1 time": "15ms", "Decision": "EXPENSIVE"},
        {"File": "sample2.c", "Key expensive fn": "—",                        "O2 time": "16ms", "O1 time": "15ms", "Decision": "CHEAP"},
        {"File": "sample3.c", "Key expensive fn": "normalize, searchMatrix",   "O2 time": "16ms", "O1 time": "15ms", "Decision": "EXPENSIVE"},
        {"File": "sample4.c", "Key expensive fn": "bubbleSort, binarySearch",  "O2 time": "15ms", "O1 time": "15ms", "Decision": "EXPENSIVE"},
        {"File": "sample5.c", "Key expensive fn": "tensorOp, deepNest, maxIn3D","O2 time":"15ms", "O1 time": "16ms", "Decision": "EXPENSIVE"},
    ]
    df_demo = pd.DataFrame(demo)
    st.dataframe(
        df_demo.style.map(
            lambda v: "background-color:#faece7;color:#993C1D;font-weight:600"
                      if v == "EXPENSIVE" else
                      ("background-color:#eaf3de;color:#3B6D11;font-weight:600" if v == "CHEAP" else ""),
            subset=["Decision"]
        ),
        use_container_width=True, hide_index=True
    )
    st.caption("Timing savings appear small on toy files because LLVM pass scheduling overhead dominates. Real savings emerge at production scale with functions of thousands of instructions.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — History
# ══════════════════════════════════════════════════════════════════════════════
elif page == "History":
    st.markdown("## Analysis history")

    if not st.session_state.history:
        st.info("No analyses yet. Go to 'Analyze code' and run your first analysis.")
    else:
        idx = st.session_state.get("selected_history", 0)
        idx = min(idx, len(st.session_state.history) - 1)

        options = [f"{h['label']} — {h['timestamp']}" for h in st.session_state.history]
        selected = st.selectbox("Select analysis", options, index=idx)
        idx = options.index(selected)
        entry = st.session_state.history[idx]

        st.divider()
        mode_html = (
            '<span class="llvm-badge">LLVM pass (exact)</span>'
            if entry["using_llvm"] else
            '<span class="est-badge">JS estimator (approximate)</span>'
        )
        st.markdown(f"**{entry['label']}** &nbsp; {mode_html} &nbsp; `{entry['timestamp']}`",
                    unsafe_allow_html=True)

        fns = entry["functions"]
        rows = []
        for f in fns:
            ft = f["features"]
            rows.append({
                "Function": f["name"],
                "Instrs": ft["instrCount"],
                "BBs": ft["basicBlocks"],
                "Loop depth": ft["loopDepth"],
                "Mem ops": ft["memOps"],
                "Types": ft["typeComplexity"],
                "Predicted (ms)": f["pred"],
                "Decision": f["decision"],
            })
        df = pd.DataFrame(rows)
        def colour_d(val):
            if val == "EXPENSIVE": return "background-color:#faece7;color:#993C1D;font-weight:600"
            return "background-color:#eaf3de;color:#3B6D11;font-weight:600"
        st.dataframe(df.style.map(colour_d, subset=["Decision"]),
                     use_container_width=True, hide_index=True)

        expensive = [f for f in fns if f["decision"] == "EXPENSIVE"]
        cheap     = [f for f in fns if f["decision"] == "CHEAP"]

        if expensive:
            st.markdown(f"""<div class="decision-box decision-exp">
            <b>Pipeline decision: EXPENSIVE — route to O1</b><br>
            Expensive functions: {', '.join(f['name'] for f in expensive)}<br>
            Cheap functions: {', '.join(f['name'] for f in cheap) or 'none'}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="decision-box decision-cheap">
            <b>Pipeline decision: CHEAP — run full O2</b><br>
            All functions are below the 4.0ms threshold.
            </div>""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Functions", len(fns))
        c2.metric("Expensive", len(expensive))
        c3.metric("Cheap", len(cheap))
        c4.metric("Peak predicted", f"{max(f['pred'] for f in fns):.1f}ms")

        with st.expander("View original code"):
            st.code(entry.get("code", ""), language="c")
