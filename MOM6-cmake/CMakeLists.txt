cmake_minimum_required(VERSION 3.15)

project(
  mom6-cmake
  VERSION 2020.07.01
  LANGUAGES C Fortran)

include(ExternalProject)
include(GNUInstallDirs)

if(NOT CMAKE_BUILD_TYPE MATCHES "^(Debug|Release|MinSizeRel|RelWithDebInfo)$")
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE "Release"
      CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
                     "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

if(NOT CMAKE_C_COMPILER_ID MATCHES "^(Intel|GNU|Clang|AppleClang)$")
  message(WARNING "Compiler not officially supported: ${CMAKE_C_COMPILER_ID}")
endif()

if(NOT CMAKE_Fortran_COMPILER_ID MATCHES "^(Intel|GNU)$")
  message(WARNING "Compiler not officially supported: ${CMAKE_Fortran_COMPILER_ID}")
endif()

option(OPENMP "Enable OpenMP threading" OFF)

ExternalProject_Add(gsw
  GIT_REPOSITORY "https://github.com/teos-10/gsw-fortran"
  GIT_TAG        "master"
  PREFIX         "${CMAKE_BINARY_DIR}/gsw"
  CMAKE_ARGS     "-DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/gsw"
                 "-DCMAKE_Fortran_COMPILER=${CMAKE_Fortran_COMPILER}"
  )

ExternalProject_Add(fms
  GIT_REPOSITORY "https://github.com/aerorahul/fms"
  GIT_TAG        "bugfix/cmake-master"
  PREFIX         "${CMAKE_BINARY_DIR}/fms"
  CMAKE_ARGS     "-DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/libFMS"
                 "-DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}"
                 "-DCMAKE_Fortran_COMPILER=${CMAKE_Fortran_COMPILER}"
                 "-DOPENMP=${OPENMP}"
                 "-D64BIT=ON" "-D32BIT=OFF"
  )

ExternalProject_Add(mom6
  GIT_REPOSITORY "https://github.com/aerorahul/mom6"
  GIT_TAG        "feature/cmake-master"
  PREFIX         "${CMAKE_BINARY_DIR}/mom6"
  CMAKE_ARGS     "-DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}/mom6"
                 "-DCMAKE_PREFIX_PATH=${CMAKE_INSTALL_PREFIX}"
                 "-DCMAKE_Fortran_COMPILER=${CMAKE_Fortran_COMPILER}"
                 "-DOPENMP=${OPENMP}"
                 "-DMOM6SOLO=ON"
  DEPENDS        gsw fms
  )
