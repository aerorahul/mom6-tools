### Data-atmosphere forcings for UFS-weather-model.
The python script [`gfs_forcings.py`](./ufs/gfs_forcings.py) is the main driver for generating the data atmosphere forcings for the ufs-weather-model (UFSWM) utilizing the CDEPS component.
The input files for `gfs_forcings.py` are:
- `sfcf000.nc` - This is the surface file produced by the UFSWM at hour 0 of the forecast (at analysis time)
- `sfcf006.nc` - This is the surface file produced by the UFSWM at hour 6 of the forecast initialized at the previous (-6H) analysis time.

The output file from `gfs_forcings.py` is:
- `forcing.nc` - This is the data-atmosphere forcings collected by reading the inputs and preparing for use with the UFSWM Data-Atmosphere application with CDEPS.

Usage for `gfs_forcings.py`:
```code
$> python3 gfs_forcings.py --help
usage: gfs_forcings.py [-h] --sfcf000 SFCF000 --sfcf006 SFCF006 [--forcing FORCING] [--debug]

Read ufs-weather-model produced surface files to generate atmospheric forcings for use with the CDEPS
component of the ufs-weather-model

optional arguments:
  -h, --help         show this help message and exit
  --sfcf000 SFCF000  sfcf000.nc at the current cycle time (default: sfcf000.nc)
  --sfcf006 SFCF006  sfcf006.nc at the current cycle time initialized 6hours ago (default: sfcf006.nc)
  --forcing FORCING  output file containing atmospheric forcings (default: forcing.nc)
  --debug            print debugging statements (default: False)
  ```
  
  The variables being mapped from `SFCF000` and `SFCF006` into `FORCING` are described in [`gfs_forcings.md`](./ufs/gfs_forcings.md)
