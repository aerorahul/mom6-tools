#!/bin/bash

set -eux

currentDate=$1 # date (YYYYMMDDHH) for which initial conditions / restarts are available
restartDir=$2  # initial conditions / restarts for the currentDate
staticDir=${3:-"./static"} # static files containing grid, mask etc.
forcDir=${4:-"./forcing"}  # atmospheric fforcing files (currently set-up for MERRA-2)
mom6Exec=${5:-"./MOM6"}    # MOM6 executable

source env

staticDir=$(cd $staticDir; pwd)
forcDir=$(cd $forcDir; pwd)
mom6Exec=$(readlink -e $mom6Exec)

y4=$(echo $currentDate | cut -c1-4)
m2=$(echo $currentDate | cut -c5-6)
d2=$(echo $currentDate | cut -c7-8)
h2=$(echo $currentDate | cut -c9-10)

tmpRunDir=mom6.run.$currentDate
[[ -d $tmpRunDir ]] && rm -rf $tmpRunDir
mkdir -p $tmpRunDir && cd $tmpRunDir
mkdir -p INPUT FORC RESTART OUTPUT

# Link the model executable
[[ -f $mom6Exec ]] && ln -sf $mom6Exec . || ( echo "$mom6Exec does not exist, ABORT!"; exit 1)

# Link the table files, and create the input namelist
ln -sf $staticDir/common/* .
sed -i "s/#YYYYMMDDHH#/$y4,$m2,$d2,$h2/g" input.nml

# Link the grid, mask, topography files
ln -sf $staticDir/fix/* INPUT/

# Link the restarts files
ln -sf $restartDir/* INPUT/

# Link the appropriate Forcing files
ln -sf $forcDir/$currentDate/* FORC/

mpirun ./MOM6
rc=$?
[[ $rc -ne 0 ]] && ( echo "MOM6 failed, ABORT!"; exit 1 ) || exit 0
