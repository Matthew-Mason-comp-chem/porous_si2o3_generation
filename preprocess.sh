#!/bin/bash

# Usage: ./preprocess.sh <Dir of interest>

# Intended to take output from CreateImage.py dir to Run Coulson ready for netmc.sh to submit jobs

set -euo pipefail
IFS=$'\n\t'
dry_run="${DRY_RUN:-false}"

# Defining directories 
export pore_evap=/u/mw/shug7609/netmc_Pores_Paper/Pore_Evaporation/
export rescale=/u/mw/shug7609/netmc_Pores_Paper/Rescale/
export dir_of_int="${1:-}"
export for_col=/u/mw/shug7609/netmc_Pores_Paper/For_Coulson/
export run_col=/u/mw/shug7609/netmc_Pores_Paper/Run_Coulson/


if [[ -z "${dir_of_int:-}" ]]; then
    echo "ERROR: You must provide the resultant folder name as the first argument."
    echo "Usage: $0 <dir_of_interest>"
    exit 2
fi


log() { printf '%s %s\n' "$(date +'%F %T')" "$*"; }

do_cmd() {
	local cmd="$1"
	if [[ "$dry_run" == "true" ]]; then
		log "[dry_run] $*"
	else
		log "$cmd"
		eval "$cmd"
	fi
}

# 0. Basic validations
if [[ ! -d "$dir_of_int" ]]; then
  echo "ERROR: Resultant folder does not exist: $RESULTANT_DIR"
  exit 3
fi

# copy to rescale
log "Copying pore_evap folder to Rescale"
do_cmd "cp -r \"$dir_of_int\" \"$rescale\" "


Work="$rescale/$(basename "$dir_of_int")"

log "Copying .py files from $rescale to $Work"
do_cmd "cp \"/u/mw/shug7609/netmc_Pores_Paper/Rescale/relax_box.in\" \"$Work\""
do_cmd "cp \"/u/mw/shug7609/netmc_Pores_Paper/Rescale/rescale.py\" \"$Work\""

# running scaling scripts 

export op=/u/mw/jesu2929/anaconda3/bin/python3

log "Running gradient descent and rescaling"
if [[ -f "$Work/relax_box.in" ]]; then
    log "Running scaling inside $Work"
    do_cmd "cd \"$Work\" && /u/mw/shug7609/lammps-2025/build/lmp -in relax_box.in"
else
    log "gradient_descent.py missing in $Work"
fi

if [[ -f "$Work/rescale.py" ]]; then
    log "Running rescale.py inside $Work"
    do_cmd "cd \"$Work\" && $op rescale.py"
else
    log "rescale.py missing in $Work"
fi


# preparing to run coulson

log "cp to for_coulson"
do_cmd "cp -r \"$Work\" \"$for_col\""

# define a new working dir 
Work="$for_col/$(basename "$dir_of_int")"
sub_results="$Work/Results"

do_cmd "mkdir -p \"$sub_results\" "
# move everything except the Results directory into Results
do_cmd "cd \"$Work\" && for f in *; do [ \"\$f\" = \"Results\" ] && continue; [ -e \"\$f\" ] || continue; mv -- \"\$f\" \"Results/\"; done"


#do_cmd "mkdir -p \"$sub_results\" "
#do_cmd "cd \"$Work\" && mv * Results"

echo "start"
log "copying input files"
do_cmd "cp /u/mw/shug7609/netmc_Pores_Paper/For_Coulson/Input/* \"$Work\""
do_cmd "cp /u/mw/shug7609/netmc_Pores_Paper/For_Coulson/Results_input/* \"$sub_results\""
echo "end"


log "Running new_netmc... .py"
if [[ -f "$sub_results/new_add_lj_to_data_file_for_coulson.py" ]]; then
    log "Running .py inside $sub_results"
    do_cmd "cd \"$sub_results\" && $op new_add_lj_to_data_file_for_coulson.py"
else
    log "python file is missing in $sub_results"
fi


# Porting to coulson
log "Copying to Run Coulson"
do_cmd "cp -r \"$Work\" \"$run_col\""
