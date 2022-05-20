#!/bin/bash

set -eu

SDATE=${1:?"Must provide a starting date [YYYYMMDDHH] to convert GMAO ocean observations"}
EDATE=${2:-$SDATE}
WINDOW_LEN=${3:-"24"}

dirOceanObs=$(pwd)/cyclingObs

IODACONVDIR="/Users/rmahajan/scratch/DATA/soca-data/GMAOobs/ioda-converters"

half_window_len=$(echo "$WINDOW_LEN / 2" | bc)
cdate=$(date -d "${SDATE:0:8} ${SDATE:8:2}" +%s)
edate=$(date -d "${EDATE:0:8} ${EDATE:8:2}" +%s)
while [[ $cdate -le $edate ]]; do

    CDATE=$(date -d "@$cdate" +%Y%m%d%H)

    echo "####################################"
    echo "converting ... $CDATE"
    echo "####################################"

    # Get a list of files within the window
    files=()
    dates=()
    datec=$(date -d "${CDATE:0:8} ${CDATE:8:2} - $half_window_len hours" +%s)
    datee=$(date -d "${CDATE:0:8} ${CDATE:8:2} + $half_window_len hours" +%s)
    while [[ $datec -lt $datee ]]; do
        DATEC=$(date -d "@$datec" +%Y%m%d%H)
        file=$dirOceanObs/geos/$DATEC/gmao-obs-${DATEC}.nc
        [[ -f $file ]] && files+=( "$file" )
        [[ -f $file ]] && dates+=( "$DATEC" )
        datec=$(date -d "${DATEC:0:8} ${DATEC:8:2} + 1 hours" +%s)
    done

    OUTDIR=$dirOceanObs/geos.ioda/${CDATE:0:8}
    mkdir -p $OUTDIR

    $IODACONVDIR/build/bin/gmao_obs2ioda.py -d $CDATE -i ${files[@]} -o $OUTDIR/gmao-obs --inputdates ${dates[@]}
    rc=$?
    [[ $rc -ne 0 ]] && ( echo "Error converting $CDATE, ABORT!"; exit 1 )

    cdate=$(date -d "${CDATE:0:8} ${CDATE:8:2} + $WINDOW_LEN hours" +%s)

done

exit 0
