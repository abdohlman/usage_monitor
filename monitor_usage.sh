#!/bin/bash
#SBATCH --mem 256Mb
#SBATCH --cpus-per-task 1
#SBATCH -o slurmlog/pathseq.slurm.%A_%a.out
#SBATCH -e slurmlog/pathseq.slurm.%A_%a.err
#SBATCH --mail-type FAIL,END --mail-user abd30@duke.edu
#SBATCH --time 00:00:00

###########################################################
# USAGE: sbatch -J m_usage --wrap "bash monitor_usage.sh" #
###########################################################

EMAIL=abd30@duke.edu
LOGFILE=./usage/usage_all.txt 
SLEEPTIME=1h

while true; do
	du --max-depth=0 /data/shenlab/* > $LOGFILE
	DT=$(date '+%d/%m/%Y %H:%M:%S')
	
	while read p; do
		USAGE=$(echo $p | awk '{print $1}')
		FILEPATH=$(echo $p | awk '{print $2}')
		USER=$(basename $FILEPATH)
		USERLOG=./usage/usage_${USER}.txt
		echo "${DT} ${USAGE}" >> $USERLOG 
	done < $LOGFILE

	du -h --max-depth=0 /data/shenlab/* > usage.txt
	
	python plot_usage.py
	
	sleep $SLEEPTIME
done


