#!/bin/bash

# Directories
export NETMC=/u/mw/shug7609/porous_si2o3_generation/Run_Coulson/
export RUNHOME=/u/mw/shug7609/porous_si2o3_generation/Run_Coulson
# Files
export X=simpleNetmc
export INPT=netmc.inpt
export SUB=netmc_sub
export AUX=/u/mw/shug7609/porous_si2o3_generation/Run_Coulson/netmc_Pores.aux
export FIXED=fixed_rings.dat
#export RESULTS=/u/mw/jesu2929/porous_si2o3_generation/Run_Coulson/run_ores/Results
# Variables
SOURCE=$( head -2 $AUX | tail -1 | awk '{print$1}')
DESTINATION=$(head -3 $AUX | tail -1 | awk '{print$1}')

CentralRing=$( head -6 $AUX | tail -1 | awk '{print$1}')
NATOMS=$( head -7 $AUX | tail -1 | awk '{print$1}')
T0=$( head -10 $AUX | tail -1 | awk '{print$1}')
T1=$( head -11 $AUX | tail -1 | awk '{print$1}')
TINC=$( head -12 $AUX | tail -1 | awk '{print$1}')

matching_dir=$(find $RUNHOME -maxdepth 1 -type d -name "Results_${CentralRing}_${NATOMS}*" | head -n 1)

printf -v NETMC "%s%s" "$matching_dir/"
printf -v RESULTS "%s%s" "${matching_dir}/Results"

#printf -v NETMC "%s%s" $RUNHOME "/Results_" $CentralRing "_" $NATOMS "_554455445544_LJ/"
#printf -v RESULTS "%s%s" $RUNHOME "/Results_" $CentralRing "_" $NATOMS "_554455445544_LJ/Results"

echo "Netmc : " $NETMC

echo "TINC : " $TINC

SEED_START=$( head -14 $AUX | tail -1 | awk '{print$1}')
SEED_END=$( head -15 $AUX | tail -1 | awk '{print$1}')

STEP=$( head -17 $AUX | tail -1 | awk '{print$1}')

ALLOWRST=$( head -19 $AUX | tail -1 | awk '{print$1}')
RUNTYPE=$( head -20 $AUX | tail -1 | awk '{print$1}')
if [ "$RUNTYPE" -eq 1 ]; then
    RUNTYPENAME="C"
elif [ "$RUNTYPE" -eq 2 ]; then
    RUNTYPENAME="TR"
else
    RUNTYPENAME=""
fi

#echo $Q
echo $T
#echo $STEP

ABST0=${T0#-}
ABST1=${T1#-}
echo $ABST0 $ABST1

T01000=`python3 -c "print('-{:10.0f}'.format(1000*$ABST0))"`
T11000=`python3 -c "print('-{:10.0f}'.format(1000*$ABST1))"`
echo $T01000 $TINC $T11000

if (( $T01000 == $T11000 ))
    then
    ABST0=${T0#-}
    ABST1=${T1#-}
elif  (( $T01000 > $T11000 ))
    then
    ABST0=${T1#-}
    ABST1=${T0#-}
fi

PORENAME=`python3 -c "print('{:.0f}'.format(100*$CentralRing))"`

# Make submission/results directories
printf -v DIR1 "%s%s%s" $DESTINATION "/Submission_" $RUNTYPENAME
printf -v DIR2 "%s%s%s" $DESTINATION "/Results_" $RUNTYPENAME
mkdir -p $DESTINATION
mkdir -p $DIR1
mkdir -p $DIR2

echo "Start Run ..." 

echo $ABST0 $TINC $ABST1
for T in `seq $ABST0 $TINC $ABST1`
do 
    echo $T
done

# Adding system to processme.txt



if [ -f "processme.txt" ]; then
    echo "processme exits"
    echo "Attempting to edit"
    printf "%s,%s,%s\n" "$CentralRing" "$NATOMS" "$STEP" >> processme.txt
else
    echo "Creating processme.txt"
    touch processme.txt
    echo "attempting to write to file"
    printf "%s,%s,%s\n" "$CentralRing" "$NATOMS" "$STEP" > processme.txt

fi



for T in `seq $ABST0 -$TINC $ABST1`
do
        echo $T
	T1000=`python3 -c "print('-{:10.8f}'.format(1000*$T))"`
        TNAME=`python3 -c "print('-{:.0f}'.format(1000*$T))"`
        echo "T = :"$TNAME



#        printf -v DIRs "%s%s%s%s" $DIR1 "/q_" $QNAME "/T_" $TNAME "/Step_" $STEP 
#        printf -v DIRr "%s%s%s%s" $DIR2 "/q_" $QNAME "/T_" $TNAME "/Step_" $STEP
#        mkdir -p $DIRs
#        mkdir -p $DIRr



        for S in `seq $SEED_START 1 $SEED_END`
        do
                restart_val=true;
	 	echo "Seed : " $S
        	printf -v DIRs "%s%s%s%s" $DIR1 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S
	        printf -v DIRr "%s%s%s%s" $DIR2 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S

		

		if [ ! -d "$DIRs" ]; then
	                printf -v DIRs "%s%s%s%s" $DIR1 "/Pore_" $CentralRing  "_" $NATOMS "/T_" $TNAME "/S_" $S "/" $STEP
        	        printf -v DIRr "%s%s%s%s" $DIR2 "/Pore_" $CentralRing  "_" $NATOMS "/T_" $TNAME "/S_" $S "/" $STEP
			restart_val=false
                else
			cd $DIRs
			folders=`ls -d */`
			var=0
			for folder in $folders
			do
			        tmp=${folder::-1}
			        if [ $tmp -gt $var ]
			        then
			            var=$tmp
			        fi
			done
			echo "Before"
 			
                        printf -v DIRs "%s%s%s%s" $DIR1 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S "/" ` expr $var + $STEP `
                        printf -v DIRr "%s%s%s%s" $DIR2 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S "/" ` expr $var + $STEP `
                        printf -v DIRr0 "%s%s%s%s" $DIR2 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S "/" $var "/Run"
                        printf -v DIRr1 "%s%s%s%s" $DIR2 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S "/" $var "/Results/"
			printf -v DIRs1 "%s%s%s%s" $DIR1 "/Pore_" $CentralRing "_" $NATOMS "/T_" $TNAME "/S_" $S "/" ` expr $var + $STEP ` "/Results"
			echo "After"
			restart_val=true

		fi
		echo $DIRs
		echo $DIRr
		echo "Directory : " $DIRr
                if [ "$ALLOWRST" -eq 0 ] && [ "$restart_val" = true ]; then
                    echo "Restarts not allowed"
		elif [ ! -d "$DIRs" ]; then

			mkdir -p $DIRs
			mkdir -p $DIRr


	                echo "New submission" $CentralRing $TNAME
        	        cp $NETMC$X $NETMC$INPT $NETMC$SUB $DIRs
                        cp $NETMC*.py $DIRs
                        echo "Restart ? : " $restart_val
			if [ "$restart_val" = false ]; then
	                	cp -r $RESULTS $DIRs
                                echo "False Restart"
			elif [ "$restart_val" = true ]; then
				cp -r $DIRr0 $DIRs1
                                echo "Copy " $DIRr0 " to " $DIRs1
				cp $DIRr1$FIXED $DIRs1
			fi

	                printf -v SUBFILE "%s%s" "R" $CentralRing "_T" $TNAME
        	        printf -v OUTFILE "%s%s%s%s" $DIRr
                	cd $DIRs
	                ls
        	        # Change submission files
                	mv $SUB $SUBFILE

	                FILENAME="sub_"$CentralRing"_"$TNAME
        	        echo $FILENAME
                	echo "++Writing to Submission File"

	                sed -i '6s|.*|#$ -N '$RUNTYPENAME'_'$CentralRing'_'$TNAME' |g' $SUBFILE
        	        sed -i '4s|.*|#$ -o '$DIRs'/%j.log |g' $SUBFILE
                	sed -i '9s|.*|export fromdir="'$DIRs'" |g' $SUBFILE
	                sed -i '10s|.*|export todir="'$DIRr'" |g' $SUBFILE
	
        	        echo "--Written Submission file"
                        if [ "$restart_val" = true ]; then
	                        sed -i '5s|.*|1               Restart Network using lammps objects? |g' $INPT
                        fi
                        sed -i '7s|.*|test            Input File prefix |g' $INPT
#			fi

			sed -i '27s|.*|'$RUNTYPE'           Selected Routine (1:SimpleGraphene,2:TriangleRaft,3:Bilayer,4:Tersoff) |g' $INPT
                   
                        sed -i '32s|.*|'$S'           random seed |g' $INPT
                        sed -i '33s|.*|0           spiral|g' $INPT
	                sed -i '38s|.*|-'$T'       start temperature (10^x) |g' $INPT
        	        sed -i '39s|.*|-'$T'       end temperature (10^x) |g' $INPT
                	sed -i '41s|.*|-'$T'       thermalisation temperature (10^x) |g' $INPT
	                sed -i '42s|.*|'$STEP'       steps per temperature |g' $INPT 
        	        sed -i '43s|.*|'$STEP'       initial thermalisation steps |g' $INPT
                	# Submit to queue
	                #sbatch $SUBFILE
                        qsub $SUBFILE
        	else
			
	                echo "Ignore repeated submission"
        	        echo $DIRs



		fi

	done
done






