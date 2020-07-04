# MOM6-cmake

`CMakeLists.txt` in this directory clones, builds and installs the dependencies of MOM6 and uses them when building MOM6 with cmake.

Usage:
```
rm -rf install
rm -rf build && mkdir -p build && cd build
cmake -DCMAKE_INSTALL_PREFIX=../install ..
make -j6
```
