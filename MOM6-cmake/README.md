# MOM6-cmake

![](https://github.com/aerorahul/mom6-tools/workflows/Build%20Linux/badge.svg)

`CMakeLists.txt` in this directory clones, builds and installs the dependencies of MOM6 and uses them when building MOM6 with cmake.

## Prerequisites:
- Intel or GNU compilers
- MPI
- NetCDF

## Environment setup (e.g. NOAA Orion)
```
module load intel
module load impi
module load netcdf # loads NETCDF_ROOT environment variable

export CC=mpiicc
export FC=mpiifort
```

## Clone and Build:
```
git clone https://github.com/aerorahul/mom6-tools

rm -rf install
rm -rf build && mkdir -p build && cd build
cmake -DCMAKE_INSTALL_PREFIX=../install ../mom6-tools/MOM6-cmake
make -j6
```
