#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-../Results_TR}"

echo "Collecting test_e_compare.out and Q_TR_engtot.out from: $ROOT"
echo

# Use -print0 to handle special chars/spaces/newlines in filenames
find "$ROOT" -type f \( -name 'test_e_compare.out' -o -name 'Q_TR_engtot.out' \) -print0 \
| while IFS= read -r -d '' file; do
    # full directory containing the file
    dir=$(dirname "$file")
    base=$(basename "$file")

    # split path into components safely
    IFS='/' read -ra parts <<< "$dir"

    # initialize
    pore="NA"; system="NA"; temp="NA"; step="NA"
    run_idx=-1
    pore_idx=-1; temp_idx=-1; system_idx=-1

    # find indices for key tokens
    for i in "${!parts[@]}"; do
        p="${parts[$i]}"
        if [[ "$p" == "Run" ]]; then
            run_idx=$i
        fi
        if [[ "$p" == Pore_* && $pore_idx -lt 0 ]]; then
            pore_idx=$i
            pore="${parts[$i]}"
        fi
        if [[ "$p" == T_* && $temp_idx -lt 0 ]]; then
            temp_idx=$i
            temp="${parts[$i]}"
        fi
        if [[ "$p" == S_* && $system_idx -lt 0 ]]; then
            system_idx=$i
            system="${parts[$i]}"
        fi
    done

    # require that Run exists and we have all the expected components
    if [[ $run_idx -lt 0 ]]; then
        echo "WARNING: file '$file' not in a 'Run' directory — skipping."
        continue
    fi
    if [[ $system_idx -lt 0 || $temp_idx -lt 0 || $pore_idx -lt 0 ]]; then
        echo "WARNING: couldn't find Pore_/T_/S_ in path for '$file' — skipping."
        continue
    fi

    # step is the directory immediately before "Run"
    if (( run_idx - 1 >= 0 )); then
        step="${parts[$((run_idx - 1))]}"
    else
        step="NA"
    fi

    # Build sanitized filename (replace any spaces with _ just in case)
    sanitize() {
        echo "$1" | tr ' ' '_' 
    }

    pore=$(sanitize "$pore")
    system=$(sanitize "$system")
    temp=$(sanitize "$temp")
    step=$(sanitize "$step")

    # Skip if pore is not 30
    if [[ "$pore" != Pore_24_1290 ]]; then
        #echo "Skipping $file :  "$pore" (pore != 30)"
        continue
    fi


    newname="${pore}_${system}_${temp}_${step}_${base}"

    # Avoid accidental overwrites: if exists, append _1 _2 ...
    if [[ -e "./$newname" ]]; then
        suffix=1
        ext="${newname##*.}"
        namebase="${newname%.*}"
        while [[ -e "./${namebase}_$suffix.$ext" ]]; do
            suffix=$((suffix+1))
        done
        newname="${namebase}_$suffix.$ext"
    fi

    # Copy preserving timestamps/permissions
    cp -p -- "$file" "./$newname"
    echo "Copied → $newname"
done

echo
echo "✅ Done."

