#!/bin/bash

set -e

NTHREADS=8
VERBOSE=OFF

topDir=$(pwd)

prefix=$topDir/install
[[ -d $prefix ]] && rm -rf $prefix

# Clone components
echo -e "\n"
echo -e "\nclone components ..."
echo -e "\n"

cd $topDir
[[ -d src ]] && rm -rf src
mkdir -p src && cd src

echo -e "\ncloning ... GSW-Fortran"
[[ -d gsw-fortran ]] && rm -rf gsw-fortran
git clone https://github.com/teos-10/gsw-fortran

echo -e "\ncloning ... FMS"
[[ -d fms ]] && rm -rf fms
git clone https://github.com/aerorahul/fms -b bugfix/cmake-master
(cd fms; git checkout 58a6305)

echo -e "\ncloning ... MOM6"
[[ -d mom6 ]] && rm -rf mom6
git clone --recursive https://github.com/aerorahul/mom6 -b feature/cmake-master
(cd mom6; git checkout f1ab18c46)

echo -e "\n"
echo -e "\nbuild components ..."
echo -e "\n"

cd $topDir

[[ -d build ]] && rm -rf build
mkdir -p build && cd build

echo -e "\nbuilding ... GSW-Fortran"
mkdir -p gsw && cd gsw
cmake -DCMAKE_INSTALL_PREFIX=$prefix/gsw $topDir/src/gsw-fortran
make -j$NTHREADS VERBOSE=$VERBOSE
make install

cd $topDir/build

echo -e "\nbuilding ... FMS"
mkdir -p fms && cd fms
cmake -DCMAKE_INSTALL_PREFIX=$prefix/fms -D32BIT=OFF -D64BIT=ON $topDir/src/fms
make -j$NTHREADS VERBOSE=$VERBOSE
make install

cd $topDir/build

echo -e "\nbuilding ... MOM6"
mkdir -p mom6 && cd mom6
cmake -DCMAKE_PREFIX_PATH=$prefix -DCMAKE_INSTALL_PREFIX=$prefix/mom6 -DMOM6SOLO=ON $topDir/src/mom6
make -j$NTHREADS VERBOSE=$VERBOSE
make install

echo -e "\ndone"
