### Description
In the tables below, the `column` headers are as follows:
- `column1`: variable names read from the GFS generated surface netCDF file
- `column2`: variable names written out in the forcing file (Fortran code)
- `column3`: mapping from the forcing file variable names to CDEPS variable names (obtained from `datm.streams`)
- `column4`: Additional notes / questions

**Questions:**
1. If CDEPS column has `Null`, does it mean that the variable is not read by CDEPS component?
These variables have no mapping into the CDEPS `datm.streams` file.

### Coordinates
| sfcf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|
| lon  |  lon | `Null` | Is this variable not used in the model? |
| lat  | lat  | `Null` | Is this variable not used in the model? |
| time | time | `Null` | Is this variable not used in the model? |


### From sfcf006.nc
| sfcf006.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|
| uflx_ave  | dusfc       | `Null`    | Is this variable not used in the model? |
| vflx_ave  | dvsfc       | `Null`    | Is this variable not used in the model? |
| prate_ave | totprcp_ave | `Null`    | Is this variable not used in the model? |
| prate_ave | precp       | Faxa_rain | `coeff * prate_ave` |
| prate_ave | fprecp      | Faxa_snow | `(1-coeff) * prate_ave` |

`coeff` calculation based on `tmp2m` in Celcius:
| `coeff` | tmp2m range |
|--|--|
| `1.0` | `tmp2m >= 0C` |
| `0.0` | `tmp2m < -15C` |
| `(tmp2m + 15.)/15.` | `0C > tmp2m > -15C` |

**Questions:**
1. Why not use `cpofp` from `sfcf006.nc` that gives "Percent frozen precipitation"?
Is there some empirical relationship here that is being accounted?

### From sfcf000.nc
| sfcf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|
| ulwrf        | ULWRF        | `Null`     | Is this variable not used in the model? |
| dlwrf        | DLWRF        | Faxa_lwdn  |
| dswrf        | DSWRF        | Faxa_swdn  |
| dswrf        | vbdsf_ave    | Faxa_swvdr | `dswrf * 0.285` |
| dswrf        | vddsf_ave    | Faxa_swvdf | `dswrf * 0.285` |
| dswrf        | nbdsf_ave    | Faxa_swndr | `dswrf * 0.215` |
| dswrf        | nddsf_ave    | Faxa_swndf | `dswrf * 0.215` |
| pressfc      | psurf        | Sa_pslv    |
| tmp2m        | t2m          | Sa_t2m     |
| spfh2m       | q2m          | Sa_q2m     |
| ugrd10m      | u10m         | Sa_u10m    |
| vgrd10m      | v10m         | Sa_v10m    |
| hgt_hyblev1  | hgt_hyblev1  | Sa_z       |
| tmp_hyblev1  | tmp_hyblev1  | Sa_tbot    |
| spfh_hyblev1 | spfh_hyblev1 | Sa_shum    |
| ugrd_hyblev1 | ugrd_hyblev1 | Sa_u       |
| vgrd_hyblev1 | vgrd_hyblev1 | Sa_v       |
| land         | slmsksfc     | Sa_mask    |
| shtfl_ave    | shtfl_ave    | `Null`     | Is this variable not used in the model? |
| lhtfl_ave    | lhtfl_ave    | `Null`     | Is this variable not used in the model? |
| icec         | icecsfc      | `Null`     | Is this variable not used in the model? |

**Questions:**
1. Why not use variables from `sfcf000.nc` for the variables that are being scaled?
What are these scaling factors?
2. `hgt_hyblev1` is a variable in the `sfcf000.nc` file.  Why not use this instead of `delz` from `atmf000.nc`?  Also, `delz` is thickness, not height. `delz` at the bottom layer is approximately twice of `hgt_hyblev1` as `hgt_hyblev1` is the mid-layer height, while `delz` will yield top-level of the layer.

### From atmf000.nc
| atmf000.nc | forcing.nc | CDEPS | Notes |
|--|--|--|--|
| See 1. | pres_hyblev1 | Sa_pbot | Pressure at hybrid level 1 |
| delz | hgt_hyblev1  | Sa_z    | Height at hybrid level 1   |

**Questions:**
1. `pres_hyblev1` is being calculated as: `pressfc * exp(-g * delz / R * tmp_hyblev1)`
Can `pres_hyblev1` be calculated from `dpres` as `sum(dpres, all levels)`
`dpres` is a 3D variable in `atmf000.nc`
2. `delz` in `atmf000.nc` is thickness (m) and not height. Also, `hyblev1` is mid-layer.  `delz` will give the top of the layer.  Why not use `hgt_hyblev1` from the `sfcf000.nc`.  If that is done, there is no need to read anything from `atmf000.nc`
