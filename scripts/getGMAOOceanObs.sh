#!/bin/bash

set -eu

SDATE=${1:?"Must provide a starting date [YYYYMMDDHH] to get ocean observations"}
EDATE=${2:-$SDATE}
WINDOW_LEN=${3:-"1"} # assimilation window (hrs)
nThreads=${4:-"2"} # Number of parallel dates to get observations

dirOceanObs=$(pwd)/cyclingObs

GEOSogcm="/discover/nobackup/rmahajan/scratch/GEOSogcm/yuri-S2S-2_1_UNSTABLE"

export ODAS_NDAYS=$(echo "$WINDOW_LEN / 2 / 24" | bc -l)
export ODAS_T_prof_sigo="10"
export ODAS_S_prof_sigo="10"
export ODAS_ADT_sigo="0.2"
export ODAS_logit_transform="False"

ODAS_OBS_TYPE="Argo CTD XBT TAO PIRATA RAMA Jason-1 Jason-2 Jason-3 Saral ERS-1 ERS-2 TOPEX GEOSAT-2 Envisat HY-2A CryoSat-2 NASA-TEAM-2"

OceanObsPY=$GEOSogcm/src/Applications/UMD_Etc/UMD_utils/ocean_obs.py
source $GEOSogcm/src/g5_modules.sh

pidList=()
i=0

cdate=$(date -d "${SDATE:0:8} ${SDATE:8:2}" +%s)
edate=$(date -d "${EDATE:0:8} ${EDATE:8:2}" +%s)

while [[ $cdate -le $edate ]]; do

  CDATE=$(date -d "@$cdate" +%Y%m%d%H)

  dirObs=$dirOceanObs/geos/$CDATE
  [[ -d $dirObs ]] && rm -rf $dirObs
  mkdir -p $dirObs && cd $dirObs

  $OceanObsPY ${CDATE:0:4} ${CDATE:4:2} ${CDATE:6:2} ${CDATE:8:2} $ODAS_OBS_TYPE &
  pid=$!
  echo "gathering $CDATE observations in process $pid"
  pidList+=($pid)
  i=$((i+1))

  if [[ $i -eq $nThreads ]]; then
    for pid in ${pidList[@]}; do
      wait $pid && echo "$pid exited normally" || echo "$pid exited abnormally with status $?"
    done
    i=0
    pidList=()
  fi

  cdate=$(date -d "${CDATE:0:8} ${CDATE:8:2} + $WINDOW_LEN hours" +%s)

done

exit 0

