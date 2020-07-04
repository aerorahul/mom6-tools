# MOM6-cmake
------------
`CMakeLists.txt` in this directory clones, builds and installs the dependencies of MOM6 and uses them when building MOM6 with cmake.

Usage:
```
module load intel impi netcdf
cmake -DCMAKE_INSTALL_PREFIX=/path/to/install/mom6/components ..
make -j6
```
