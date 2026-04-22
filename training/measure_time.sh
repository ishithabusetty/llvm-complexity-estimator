#!/bin/bash
# measure_time.sh — extract features and assign weighted per-function compile time
# Weights time by instruction count so complex functions get more of the budget

set -e
PASS_SO=~/llvm-complexity-estimator/pass/build/libComplexityPass.so
OUT=~/llvm-complexity-estimator/features_timed.csv
TRAINING_DIR=~/llvm-complexity-estimator/training

echo "function,instrCount,basicBlocks,loopDepth,phiNodes,memOps,typeComplexity,compileTime_ms" > "$OUT"

for c_file in "$TRAINING_DIR"/sample*.c; do
    base=$(basename "$c_file" .c)
    ll_file="$TRAINING_DIR/${base}.ll"

    # Compile to LLVM IR
    clang -O0 -emit-llvm -S "$c_file" -o "$ll_file"

    # Extract features
    features=$(opt -load-pass-plugin "$PASS_SO" \
        -passes="complexity-pass" -disable-output "$ll_file" 2>&1)

    [ -z "$features" ] && echo "WARNING: no output for $base" && continue

    # Time the O2 pipeline for this file (3 runs, take minimum for stability)
    best_ms=99999
    for run in 1 2 3; do
        start_ms=$(date +%s%3N)
        opt -O2 -disable-output "$ll_file" 2>/dev/null
        end_ms=$(date +%s%3N)
        elapsed=$((end_ms - start_ms))
        [ "$elapsed" -lt "$best_ms" ] && best_ms=$elapsed
    done
    [ "$best_ms" -eq 0 ] && best_ms=1

    # Compute total instruction count for this file (for weighting)
    total_instrs=$(echo "$features" | awk -F',' '{s+=$2} END{print s}')
    [ "$total_instrs" -eq 0 ] && total_instrs=1

    echo "Processing $base: ${best_ms}ms total, ${total_instrs} total instrs"

    # Write each function with instruction-weighted time
    while IFS=',' read -r fn instrs bbs depth phi mem tcomp; do
        [ -z "$fn" ] && continue
        # Weight: function's share of instructions * total file time
        # Use awk for float arithmetic, round to integer, minimum 1ms
        weighted=$(awk -v instrs="$instrs" -v total="$total_instrs" \
                       -v total_ms="$best_ms" \
                       'BEGIN {
                           w = (instrs / total) * total_ms;
                           r = int(w + 0.5);
                           if (r < 1) r = 1;
                           print r
                       }')
        echo "${fn},${instrs},${bbs},${depth},${phi},${mem},${tcomp},${weighted}" >> "$OUT"
        echo "  $fn: instrs=$instrs → ${weighted}ms"
    done <<< "$features"

    echo ""
done

echo "Done! Output saved to $OUT"
echo ""
cat "$OUT"
