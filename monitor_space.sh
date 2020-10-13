#!/bin/bash
#SBATCH --mem 256Mb
#SBATCH --cpus-per-task 1
#SBATCH -o slurmlog/pathseq.slurm.%A_%a.out
#SBATCH -e slurmlog/pathseq.slurm.%A_%a.err
#SBATCH --mail-type FAIL,END --mail-user abd30@duke.edu
#SBATCH --time 00:00:00

###########################################################
# USAGE: sbatch -J m_space --wrap "bash monitor_space.sh" #
###########################################################

EMAIL=abd30@duke.edu
LOGFILE=capacity_log.txt
REPORT=usage_report.pdf

while true; do
	DT=$(date '+%d/%m/%Y %H:%M:%S')
	USAGE=$(df /data/shenlab/ | sed -n 2p | awk '{print $3}')
	PCTFULL=$(df /data/shenlab/ | sed -n 2p | awk '{print $5}')
	NUMPCTFULL=${PCTFULL//%/}
	echo "${DT} ${PCTFULL} ${USAGE}" >> $LOGFILE

	BODY="Sent ${DT}."

	if [ $NUMPCTFULL -ge 99 ]; then
		SUBJECT="CRITICAL: HARDAC is full, killing jobs"
		echo $BODY | mail -s $SUBJECT $EMAIL -A $REPORT	
		scancel -t PENDING
	elif [ $NUMPCTFULL -ge 95 ]; then
		MESSAGE="DANGER: HARDAC at $PCTFULL capacity!"
		echo $BODY | mail -s $SUBJECT $EMAIL -A $REPORT
		SLEEPTIME=4h
	elif [ $NUMPCTFULL -ge 90 ]; then
		MESSAGE="WARNING: HARDAC at $PCTFULL capacity!"
		echo $BODY | mail -s $SUBJECT $EMAIL -A $REPORT
		SLEEPTIME=4h
	else
		SLEEPTIME=1h
	fi

	sleep $SLEEPTIME
done




