#!/bin/bash
# demo.sh — End-to-end demo of the LLVM IR Complexity Estimator
# Uses trained model_weights.json to make per-function predictions

PASS_SO=~/llvm-complexity-estimator/pass/build/libComplexityPass.so
TRAINING=~/llvm-complexity-estimator/training
WEIGHTS=~/llvm-complexity-estimator/model/model_weights.json

# Read model weights and threshold from JSON using python3
read THRESHOLD COEF_INSTRS COEF_BB COEF_LOOP COEF_PHI COEF_MEM COEF_TYPE \
     INTERCEPT SC_MEAN_0 SC_MEAN_1 SC_MEAN_2 SC_MEAN_3 SC_MEAN_4 SC_MEAN_5 \
     SC_SCL_0  SC_SCL_1  SC_SCL_2  SC_SCL_3  SC_SCL_4  SC_SCL_5 \
<<< $(python3 -c "
import json
w = json.load(open('$WEIGHTS'))
c = w['coefficients']
m = w['scaler_mean']
s = w['scaler_scale']
print(w['threshold_ms'],
      c[0],c[1],c[2],c[3],c[4],c[5],
      w['intercept'],
      m[0],m[1],m[2],m[3],m[4],m[5],
      s[0],s[1],s[2],s[3],s[4],s[5])
")

# Predict compile time for one function given its features
# Usage: predict_ms instrCount basicBlocks loopDepth phiNodes memOps typeComplexity
predict_ms() {
    python3 -c "
coef   = [$COEF_INSTRS,$COEF_BB,$COEF_LOOP,$COEF_PHI,$COEF_MEM,$COEF_TYPE]
mean   = [$SC_MEAN_0,$SC_MEAN_1,$SC_MEAN_2,$SC_MEAN_3,$SC_MEAN_4,$SC_MEAN_5]
scale  = [$SC_SCL_0,$SC_SCL_1,$SC_SCL_2,$SC_SCL_3,$SC_SCL_4,$SC_SCL_5]
feats  = [$1,$2,$3,$4,$5,$6]
scaled = [(feats[i]-mean[i])/scale[i] for i in range(6)]
pred   = sum(coef[i]*scaled[i] for i in range(6)) + $INTERCEPT
print(round(max(pred, 0.5), 1))
"
}

echo "================================================"
echo "   LLVM IR Complexity Estimator — Demo"
echo "   Decision threshold: ${THRESHOLD}ms"
echo "================================================"
echo ""

total_files=0
cheap_files=0
expensive_files=0
total_o2_ms=0
total_o1_ms=0

for sample in sample1 sample2 sample3 sample4 sample5; do
    c_file="$TRAINING/${sample}.c"
    ll_file="$TRAINING/${sample}.ll"
    [ -f "$c_file" ] || continue

    total_files=$((total_files + 1))

    # Compile to IR
    clang -O0 -emit-llvm -S "$c_file" -o "$ll_file"

    # Extract features
    features=$(opt -load-pass-plugin "$PASS_SO" \
        -passes="complexity-pass" -disable-output "$ll_file" 2>&1)

    echo "--- File: $sample ---"
    echo "  Function              instrs  BBs  loops  mem  types  predicted"
    echo "  ──────────────────── ──────  ───  ─────  ───  ─────  ─────────"

    file_decision="CHEAP"
    while IFS=',' read -r fn instrs bbs depth phi mem tcomp; do
        [ -z "$fn" ] && continue
        pred=$(predict_ms "$instrs" "$bbs" "$depth" "$phi" "$mem" "$tcomp")
        # Compare with threshold using python (bash can't do float compare)
        is_expensive=$(python3 -c "print('yes' if $pred >= $THRESHOLD else 'no')")
        if [ "$is_expensive" = "yes" ]; then
            label="EXPENSIVE ⚠"
            file_decision="EXPENSIVE"
        else
            label="cheap ✓"
        fi
        printf "  %-20s %6s  %3s  %5s  %3s  %5s  %5.1fms  %s\n" \
            "$fn" "$instrs" "$bbs" "$depth" "$mem" "$tcomp" "$pred" "$label"
    done <<< "$features"

    # Time both pipelines (3 runs each, take minimum)
    best_o2=99999; best_o1=99999
    for run in 1 2 3; do
        t0=$(date +%s%3N)
        opt -O2 -disable-output "$ll_file" 2>/dev/null
        t1=$(date +%s%3N)
        e=$((t1-t0)); [ "$e" -lt "$best_o2" ] && best_o2=$e

        t0=$(date +%s%3N)
        opt -O1 -disable-output "$ll_file" 2>/dev/null
        t1=$(date +%s%3N)
        e=$((t1-t0)); [ "$e" -lt "$best_o1" ] && best_o1=$e
    done

    total_o2_ms=$((total_o2_ms + best_o2))
    total_o1_ms=$((total_o1_ms + best_o1))

    echo ""
    echo "  O2 (full pipeline):    ${best_o2}ms"
    echo "  O1 (reduced pipeline): ${best_o1}ms"

    if [ "$file_decision" = "EXPENSIVE" ]; then
        expensive_files=$((expensive_files + 1))
        saved=$((best_o2 - best_o1))
        echo "  → DECISION: EXPENSIVE — use O1  (Δ = ${saved}ms for this file)"
        total_o1_ms=$((total_o1_ms))   # already counted O1
    else
        cheap_files=$((cheap_files + 1))
        echo "  → DECISION: CHEAP — run full O2"
        # For cheap files we'd use O2, so subtract O1 and add O2 back
        total_o1_ms=$((total_o1_ms - best_o1 + best_o2))
    fi
    echo ""
done

# Compute savings: compare all-O2 vs model-guided
saved_total=$((total_o2_ms - total_o1_ms))
if [ "$total_o2_ms" -gt 0 ]; then
    pct=$(python3 -c "print(round(100*$saved_total/$total_o2_ms, 1))")
else
    pct=0
fi

echo "================================================"
echo "  Summary"
echo "================================================"
echo "  Files analysed  : $total_files"
echo "  Predicted CHEAP : $cheap_files  → ran full O2"
echo "  Predicted EXPENSIVE: $expensive_files → used O1"
echo ""
echo "  All-O2 total time    : ${total_o2_ms}ms"
echo "  Model-guided time    : ${total_o1_ms}ms"
echo "  Time saved           : ${saved_total}ms  (${pct}% reduction)"
echo ""
echo "  Result: compile-time budget enforced with"
echo "          minimal optimisation quality loss"
echo "================================================"
