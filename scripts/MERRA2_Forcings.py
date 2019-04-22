#!/usr/bin/env python

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import datetime as dt
import numpy as np
import os
import socket
import shutil
import xarray as xr
import pandas as pd


def getMERRA2stream(cdate):

    # MERRA2 streams starting dates
    d1 = dt.datetime.strptime('19800101', '%Y%m%d').date()
    d2 = dt.datetime.strptime('19920101', '%Y%m%d').date()
    d3 = dt.datetime.strptime('20010101', '%Y%m%d').date()
    d4 = dt.datetime.strptime('20110101', '%Y%m%d').date()

    today = dt.datetime.today().date()

    if d1 <= cdate < d2:
        stream = 'MERRA2_100'
    elif d2 <= cdate < d3:
        stream = 'MERRA2_200'
    elif d3 <= cdate < d4:
        stream = 'MERRA2_300'
    elif d4 <= cdate < today:
        stream = 'MERRA2_400'
    else:
        raise ValueError('MERRA2 date is out of range {:%Y%m%d}'.format(cdate))

    return stream


def timeAverage(da_in, freq):

    df = da_in.to_dataframe()

    level_names = list(df.index.names)

    level_values = df.index.get_level_values

    ind_time = level_names.index('time')
    ind_lat = level_names.index('lat')
    ind_lon = level_names.index('lon')

    freqH = '{}H'.format(freq)

    df_avg = df.groupby([pd.Grouper(freq=freqH, level=ind_time)] +
                        [level_values(i) for i in [ind_lat, ind_lon]]).mean()

    da_out = df_avg.to_xarray()

    da_out.lat.attrs = da_in.lat.attrs
    da_out.lon.attrs = da_in.lon.attrs
    da_out.time.attrs = da_in.time.attrs
    da_out[da_in.name].attrs = da_in.attrs

    return da_out


def readMERRA2(fname, varname):

    DS = xr.open_dataset(fname)
    da = DS.get(varname)
    DS.close()

    return da


def check_path_exists(fname):

    if not os.path.exists(fname):
        raise FileNotFoundError('{0} does not exist!'.format(fname))

    return


if __name__ == "__main__":

    host = socket.gethostname()
    if host.startswith('discover'):
        dir_MERRA2 = "/discover/nobackup/projects/gmao/merra2"
        lMERRA2 = False
    else:
        dir_MERRA2 = None
        lMERRA2 = True

    description = "Fetch and create MERRA2 Forcings for MOM6"
    outdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                             '/../DATA/fluxes/merra2')

    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--date', help='date to create MERRA2 forcings for MOM6', metavar='YYYYMMDD', type=str, required=True)
    parser.add_argument('--outdir', help='directory to save final forcings to', type=str, default=outdir, required=False)
    parser.add_argument('--tavg_rad', help='time-averaging frequency for Radiation forcings (hours)', type=int, default=12, required=False)
    parser.add_argument('--tavg_met', help='time-averaging frequency for Meteorological forcings (hours)', type=int, default=6, required=False)
    parser.add_argument('--MERRA2dir', help='directory containing MERRA2 dataset', type=str, required=lMERRA2, default=dir_MERRA2)
    parser.add_argument('--tavg_pcp', help='time-averaging frequency for Precipitation forcings (hours)', type=int, default=24, required=False)

    args = parser.parse_args()

    cdatestr = args.date
    cdate = dt.datetime.strptime(cdatestr, '%Y%m%d').date()
    outdir = os.path.realpath(args.outdir)
    tavg_rad = args.tavg_rad
    tavg_met = args.tavg_met
    tavg_pcp = args.tavg_pcp
    dir_MERRA2 = args.MERRA2dir

    outdir = outdir + '/{0:.4}/{0}'.format(cdatestr)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    stream = getMERRA2stream(cdate)

    pth = '{}/data/products/{}/{:Y%Y/M%m}'.format(dir_MERRA2, stream, cdate)
    check_path_exists(pth)

    rad = '{}/{}.tavg1_2d_rad_Nx.{:%Y%m%d}.nc4'.format(pth, stream, cdate)
    check_path_exists(rad)
    asm = '{}/{}.inst1_2d_asm_Nx.{:%Y%m%d}.nc4'.format(pth, stream, cdate)
    check_path_exists(asm)
    flx = '{}/{}.tavg1_2d_flx_Nx.{:%Y%m%d}.nc4'.format(pth, stream, cdate)
    check_path_exists(flx)

    # Read MERRA2
    swgnt = readMERRA2(rad, 'SWGNT')
    lwgnt = readMERRA2(rad, 'LWGNT')

    u10m = readMERRA2(asm, 'U10M')
    v10m = readMERRA2(asm, 'V10M')
    t2m = readMERRA2(asm, 'T2M')
    qv10m = readMERRA2(asm, 'QV10M')

    prectot = readMERRA2(flx, 'PRECTOT')

    # Do time-averaging
    tavg_swgnt = timeAverage(swgnt, tavg_rad)
    tavg_lwgnt = timeAverage(lwgnt, tavg_rad)

    tavg_u10m = timeAverage(u10m, tavg_met)
    tavg_v10m = timeAverage(v10m, tavg_met)
    tavg_t2m = timeAverage(t2m, tavg_met)
    tavg_qv10m = timeAverage(qv10m, tavg_met)

    tavg_prectot = timeAverage(prectot, tavg_pcp)

    # Write to netCDF
    tavg_swgnt.to_netcdf(path=outdir+'/'+'SWGNT.nc4', mode='w')
    tavg_lwgnt.to_netcdf(path=outdir+'/'+'LWGNT.nc4', mode='w')
    tavg_u10m.to_netcdf(path=outdir+'/'+'U10M.nc4', mode='w')
    tavg_v10m.to_netcdf(path=outdir+'/'+'V10M.nc4', mode='w')
    tavg_t2m.to_netcdf(path=outdir+'/'+'T2M.nc4', mode='w')
    tavg_qv10m.to_netcdf(path=outdir+'/'+'QV10M.nc4', mode='w')
    tavg_prectot.to_netcdf(path=outdir+'/'+'PRECTOT.nc4', mode='w')