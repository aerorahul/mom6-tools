# MOM6-examples

- `buildMOM6Ex.sh` build's `MOM6` executable in `ocean_only` or `ocean_sis2` mode using the procedure outlined in MOM6-Examples.
- `buildMOM6cmake.sh` build's `MOM6` library and executable in `ocean_only` and optionally `ocean_sis2` mode using `cmake` -- **`DEPRECATED`**.  See [README.md](../MOM6-cmake/README.md).
- To run the tests, soft-link `MOM6-testing` as `.datasets` in `INPUT` directory for the specific
example.

- `runMOM6.sh` is an example script to run a standalone MOM6 in `ocean_sis2` mode. It has been tested for 1 degree on discover.

```bash
$> tree -L 2 static
static
├── common
│   ├── MOM_input
│   ├── MOM_resolution
│   ├── SIS_input
│   ├── SIS_resolution
│   ├── data_table
│   ├── diag_table
│   ├── field_table
│   └── input.nml
└── fix
    ├── atmos_mosaic_tile1Xland_mosaic_tile1.nc
    ├── atmos_mosaic_tile1Xocean_mosaic_tile1.nc
    ├── chl.nc
    ├── grid_spec.nc
    ├── hycom1_75_800m.nc
    ├── land_mask.nc
    ├── land_mosaic_tile1Xocean_mosaic_tile1.nc
    ├── layer_coord.nc
    ├── ocean_hgrid.nc
    ├── ocean_mask.nc
    ├── ocean_mosaic.nc
    ├── ocean_topog.nc
    ├── sgs_h2.nc
    ├── tideamp.nc
    └── topog.nc -> ocean_topog.nc
```

```bash
$> tree -L 2 forcing
forcing
├── 2015120212
│   ├── LWGNT.nc
│   ├── PRECTOT.nc
│   ├── QV2M.nc
│   ├── SLP.nc
│   ├── SWGNT.nc
│   ├── T2M.nc
│   ├── U10M.nc
│   └── V10M.nc
└── 2015120312
    ├── LWGNT.nc
    ├── PRECTOT.nc
    ├── QV2M.nc
    ├── SLP.nc
    ├── SWGNT.nc
    ├── T2M.nc
    ├── U10M.nc
    └── V10M.nc
```

```bash
$> tree -L 2 restartICs
restartICs
├── MOM.res.nc
├── calving.res.nc
├── coupler.res
├── ice_model.res.nc
└── icebergs.res.nc
```
