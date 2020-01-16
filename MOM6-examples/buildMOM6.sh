#!/bin/bash

set +x

# Usage
usage() { echo "Usage: $(basename $0) [osx-gnu.mk | nccs-intel.mk | theia-intel.mk] [fms | ocean_only | ocean_sis2]" 1>&2; exit 1; }

abort() { echo "$1: ABORT!"; exit 1; }
# FMS
function fms() {

    echo "############"
    echo "Building FMS"
    echo "############"

    cd $dirROOT
    cwd=$(pwd)

    [[ -d build/$compiler/shared/repro ]] && rm -rf build/$compiler/shared/repro;
    mkdir -p build/$compiler/shared/repro;

    cd $cwd/build/$compiler/shared/repro;
    ../../../../src/mkmf/bin/list_paths \
    -l ../../../../src/FMS;
    [[ $? -ne 0 ]] && abort "FMS"

    cd $cwd/build/$compiler/shared/repro;
    ../../../../src/mkmf/bin/mkmf \
    -t ../../../../src/mkmf/templates/$template \
    -p libfms.a \
    -c "$FMS_CPPDEFS" \
    path_names;
    [[ $? -ne 0 ]] && abort "FMS"

    cd $cwd/build/$compiler/shared/repro;
    make NETCDF=3 REPRO=1 libfms.a -j;
    [[ $? -ne 0 ]] && abort "FMS"

}

# MOM6 only
function ocean_only() {

    echo "#############"
    echo "Building MOM6"
    echo "#############"

    cd $dirROOT
    cwd=$(pwd)

    [[ -d build/$compiler/ocean_only/repro ]] && rm -rf build/$compiler/ocean_only/repro;
    mkdir -p build/$compiler/ocean_only/repro;

    cd $cwd/build/$compiler/ocean_only/repro;
    ../../../../src/mkmf/bin/list_paths \
    -l ./ ../../../../src/MOM6/config_src/{dynamic,solo_driver} \
       ../../../../src/MOM6/src/{*,*/*}/;
    [[ $? -ne 0 ]] && abort "MOM6"

    cd $cwd/build/$compiler/ocean_only/repro;
    ../../../../src/mkmf/bin/mkmf \
    -t ../../../../src/mkmf/templates/$template \
    -o "-I../../shared/repro" \
    -p MOM6 -l "-L../../shared/repro -lfms" \
    -c "$FMS_CPPDEFS" \
    path_names;
    [[ $? -ne 0 ]] && abort "MOM6"

    cd $cwd/build/$compiler/ocean_only/repro;
    make NETCDF=3 REPRO=1 MOM6 -j;
    [[ $? -ne 0 ]] && abort "MOM6"

}

# MOM6+SIS2
function ocean_sis2() {

    echo "##################"
    echo "Building MOM6+SIS2"
    echo "##################"

    cd $dirROOT
    cwd=$(pwd)

    [[ -d build/$compiler/ocean_sis2/repro ]] && rm -rf build/$compiler/ocean_sis2/repro;
    mkdir -p build/$compiler/ocean_sis2/repro;

    cd $cwd/build/$compiler/ocean_sis2/repro;
    ../../../../src/mkmf/bin/list_paths \
    -l ./ ../../../../src/MOM6/config_src/{dynamic,coupled_driver} \
       ../../../../src/MOM6/src/{*,*/*}/ ../../../../src/{atmos_null,coupler,land_null,ice_ocean_extras,icebergs,SIS2,FMS/coupler,FMS/include}/;
    [[ $? -ne 0 ]] && abort "MOM6+SIS2"

    cd $cwd/build/$compiler/ocean_sis2/repro;
    /../../../src/mkmf/bin/mkmf \
    -t ../../../../src/mkmf/templates/$template \
    -o "-I../../shared/repro" \
    -p MOM6 \
    -l "-L../../shared/repro -lfms" \
    -c "$FMS_CPPDEFS -Duse_AM3_physics -D_USE_LEGACY_LAND_" \
    path_names;
    [[ $? -ne 0 ]] && abort "MOM6+SIS2"

    cd $cwd/build/$compiler/ocean_sis2/repro;
    ../../../../src/mkmf/bin/mkmf \
    -t ../../../../src/mkmf/templates/$template \
    -o "-I../../shared/repro" \
    -p MOM6 \
    -l "-L../../shared/repro -lfms" \
    -c "$FMS_CPPDEFS" \
    path_names;
    [[ $? -ne 0 ]] && abort "MOM6+SIS2"

    cd $cwd/build/$compiler/ocean_sis2/repro;
    make NETCDF=3 REPRO=1 MOM6 -j;
    [[ $? -ne 0 ]] && abort "MOM6+SIS2"

}

# Gather user input
template=${1:-"osx-gnu.mk"}
build=${2:-"fms"}

# Grab compiler from user provided template
compiler=$(echo $template | cut -d"-" -f2 | cut -d"." -f1)

# Root directory of MOM6-examples
dirROOT=$(pwd)

FMS_CPPDEFS="-Duse_libMPI -Duse_netCDF -DSPMD"

# Build FMS
fms $template

# Build MOM6 (+ options)
if [ "$build" == "ocean_only" ]; then
    ocean_only $template
elif [ "$build" == "ocean_sis2" ]; then
    ocean_sis2 $template
else
    [[ "$build" == "fms" ]] || ( echo "Unknown build $build"; usage ; exit 1 )
fi

exit 0
