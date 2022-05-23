### Description
In the tables below, the `column` headers are as follows:
- `column1`: variable names read from the GFS generated surface flux grib2 file
- `column2`: variable names read from the GFS generated surface netCDF file
- `column3`: variable names written out in the forcing file (Fortran code)
- `column4`: mapping from the forcing file variable names to CDEPS variable names (obtained from `datm.streams`)
- `column5`: Additional notes / questions

**Questions:**
1. If CDEPS column has `Null`, means that the variable is not read by CDEPS component.
These variables have no mapping into the CDEPS `datm.streams` file.

### Coordinates
|sfluxf000.grib2| sfcf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|--|
|| lon  |  lon | `Null` | This variable is not read by CDEPS |
|| lat  | lat  | `Null` | This variable is not read by CDEPS |
|| time | time | `Null` | This variable is not read by CDEPS |


### From sfluxf006.grib2 / sfcf006.nc
|sfluxf006.grib2| sfcf006.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|--|
|UFLX@surface | uflx_ave  | dusfc       | `Null`    | This variable is not read by CDEPS |
|VFLX@surface | vflx_ave  | dvsfc       | `Null`    | This variable is not read by CDEPS |
|PRATE@surface| prate_ave | totprcp_ave | `Null`    | This variable is not read by CDEPS |
|PRATE@surface| prate_ave | precp       | Faxa_rain | `coeff * prate_ave` |
|PRATE@surface| prate_ave | fprecp      | Faxa_snow | `(1-coeff) * prate_ave` |

`coeff` calculation based on `tmp2m` in Celcius:
| `coeff` | tmp2m range |
|--|--|
| `1.0` | `tmp2m >= 0C` |
| `0.0` | `tmp2m < -15C` |
| `(tmp2m + 15.)/15.` | `0C > tmp2m > -15C` |

**Questions:**
1. `precp` and `fprecp` are the liquid and frozen precipitation rates respectively.  GFSv16 `sfcf006.nc` contains a variable `cpofp` as the `Percent frozen precipitation`.  Why not use `cpofp` to derive `precp` and `fprecp` from `prate_ave` instead of the empirical relationship with `tmp2m`?

### From sfluxf000.grib2 / sfcf000.nc
|sfluxf000.grib2| sfcf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|--|
|ULWRF@surface   | ulwrf        | ULWRF        | `Null`     | This variable is not read by CDEPS |
|DLWRF@surface   | dlwrf        | DLWRF        | Faxa_lwdn  |
|DSWRF@surface   | dswrf        | DSWRF        | Faxa_swdn  |
|DSWRF@surface   | dswrf        | vbdsf_ave    | Faxa_swvdr | `dswrf * 0.285` |
|DSWRF@surface   | dswrf        | vddsf_ave    | Faxa_swvdf | `dswrf * 0.285` |
|DSWRF@surface   | dswrf        | nbdsf_ave    | Faxa_swndr | `dswrf * 0.215` |
|DSWRF@surface   | dswrf        | nddsf_ave    | Faxa_swndf | `dswrf * 0.215` |
|PRES@surface    | pressfc      | psurf        | Sa_pslv    |
|TMP@2m          | tmp2m        | t2m          | Sa_t2m     |
|SPFH@2m         | spfh2m       | q2m          | Sa_q2m     |
|UGRD@10m        | ugrd10m      | u10m         | Sa_u10m    |
|VGRD@10m        | vgrd10m      | v10m         | Sa_v10m    |
|HGT@hybrid_lev1 | hgt_hyblev1  | hgt_hyblev1  | Sa_z       |
|TMP@hybrid_lev1 | tmp_hyblev1  | tmp_hyblev1  | Sa_tbot    |
|SPFH@hybrid_lev1| spfh_hyblev1 | spfh_hyblev1 | Sa_shum    |
|UGRD@hybrid_lev1| ugrd_hyblev1 | ugrd_hyblev1 | Sa_u       |
|VGRD@hybrid_lev1| vgrd_hyblev1 | vgrd_hyblev1 | Sa_v       |
|LAND@surface    | land         | slmsksfc     | Sa_mask    |
|SHTFL@surface   | shtfl_ave    | shtfl_ave    | `Null`     | This variable is not read by CDEPS |
|LHTFL@surface   | lhtfl_ave    | lhtfl_ave    | `Null`     | This variable is not read by CDEPS |
|ICEC@surface    | icec         | icecsfc      | `Null`     | This variable is not read by CDEPS |

**Questions:**
1. GFSv16 surface netCDF files e.g. `sfcf000.nc` contains the variables `vbdsf_ave`, `vddsf_ave`, `nbdsf_ave`, `nddsf_ave`. Why not use those variables directly instead of scaling them empirically and deriving them from `dswrf`?  What are these scaling factors?
2. `hgt_hyblev1` is being derived using `delz` at the lowest level from `atmf000.nc`.  `HGT@hybrid_lev1` is available in `sfluxf000.grib2` file.   `hgt_hyblev1` is also available in `sfcf000.nc` file. Why not use it directly instead of using `delz`.  Also, `delz` is thickness, not height. `delz` at the bottom layer is approximately twice of `hgt_hyblev1` as `hgt_hyblev1` is the mid-layer height, while `delz` will yield top-level of the layer.

### From atmf000.nc
|| atmf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|--|
|| See 1. | pres_hyblev1 | Sa_pbot | Pressure at hybrid level 1 |
|| delz | hgt_hyblev1  | Sa_z    | Height at hybrid level 1   |

**Questions:**
1. `pres_hyblev1` is being calculated as: `pressfc * exp(-g * delz / R * tmp_hyblev1)`.  `delz` is thickness at the value is at the top of the layer.  Is it appropriate to calculate pressure at the mid-layer (`pres_hyblev1`) using `delz` at the top of the layer?  Should the formula be: `pressfc * exp(-g * hgt_hyblev1 / R * tmp_hyblev1)`?
2. Calculating from `hgt_hyblev1` and using `HGT@hybrid_lev1` from `sfluxf000.grib2` or `hgt_hyblev1` from `sfcf000.nc` will eliminate the need for using `atmf000.nc` completely.
