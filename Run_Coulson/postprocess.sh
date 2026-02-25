#!/bin/bash

# Define Python interpreter
python_exec=/u/mw/jesu2929/anaconda3/bin/python3

# python scripts
q_ana="Q_eval_TR.py"
theta_ana="TR_shells_theta.py"

# read processme.txt then loop through systems 
# re naming to prevent other scripts adding to processme being an issue - name can be based on time of day hence multiple postprocessme
# can be run at the same time
# step 1 generate new file name
filename="output_$(date +%Y%m%d_%H%M%S).txt"
echo $filename

processfile="$filename"

mv "processme.txt" "$processfile"



while IFS=", " read -r CentralRing NAtoms STEPS; do
	echo "Prcoessing Pore_$CentralRing _ $NAtoms $STEPS"
		
	dir="Results_TR/Pore_${CentralRing}_$NAtoms"
	
	# Running electrostatic analysis (fast hence first)
	echo "--------------------------------------------------"
        echo "Copying $q_ana and running in directory: $dir"
	
	cp "Results_TR/$q_ana" "$dir"
	cd "$dir" || continue
	
	# Passing number of steps as an argument or ???
	$python_exec Q_eval_TR.py --steps $STEPS

	cd ../..
	
	echo "electrostatic analysis complete"

	# Running Theta, radius analaysis (geometric analysis)
	echo "--------------------------------------------------"
	echo "Copying $theta_ana and running in dir: $dir"
	
	cp "Results_TR/$theta_ana" "$dir"
	cd "$dir" || continue

        # Passing number of steps as an argument
	$python_exec TR_shells_theta.py --steps $STEPS
	cd ../..

	echo "Geometric analysis complete"

	# delting dump files
	echo "--------------------------------------------------"
	cd "$dir" || continue
	
	rm T_-*/S_*/*/Si_dump.lammpstrj
	rm T_-*/S_*/*/Si2O3_dump.lammpstrj
	
	cd ../..

	echo "all dump files deleted"
	
	# compressing into zip (based on zip_ematrix_log.sh)
       	echo "--------------------------------------------------"
	echo "Compressing largre files"
	
	LOGFILE="${dir}/zip_ematrix_log.log"		
	echo "[$(date)] Starting compression in $dir" | tee -a "$LOGFILE"
	
	# find all subdirs recurively
	find "$dir" -type d | while read -r di; do
		file1="$di/log.lammps"
		file2="$di/Run/test_ematrix.out"
		
		# both files must exist
		if [[ -f "$file1" && -f "$file2" ]]; then
			zipfile="$di/ematrix_log.zip"
			
			# skip if already zipped
			if [[ -f "$zipfile" ]]; then
				echo"[$(date)] Skipping $dir (already zipped)" | tee -a "$LOGFILE"
		                continue
			fi

			echo "[$(date)] Zipping in $di ..." | tee -a "$LOGFILE"
		        if zip -q -9 "$zipfile" "$file1" "$file2"; then
            			if unzip -tq "$zipfile" >/dev/null 2>&1; then
                			echo "[$(date)] Zip verified, removing originals in $di" | tee -a "$LOGFILE"
                			rm -f "$file1" "$file2"
            			else
                			echo "[$(date)] Zip test failed in $di — originals kept" | tee -a "$LOGFILE"
                			rm -f "$zipfile"
            			fi
        		else
            			echo "[$(date)] Zip failed in $di" | tee -a "$LOGFILE"
	        	fi
		else
			echo "File doesn't appear to exist"

		fi
	done

	echo "[$(date)] Completed compression in $di" | tee -a "$LOGFILE"



done < $processfile



while IFS=", " read -r CentralRing NAtoms STEPS; do
	echo "excuting tr_shells.py"
	 # Running topological analysis
        echo "-------------------------------------------------------------------------------------------------------"
        echo "-------------------------------------------------------------------------------------------------------"

        cd "$dir" || continue
        cp ../TR_shells.py .

        $python_exec TR_shells.py --steps $STEPS

        cd ../..


        # Removing entry from processme.txt
        sed -i "\|^$CentralRing, *$NAtoms, *$STEPS$|d" $processfile


done < $processfile

rm $processfile
