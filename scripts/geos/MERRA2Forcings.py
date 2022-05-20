#!/usr/bin/env python

import os, sys, socket
import multiprocessing
from datetime import datetime, timedelta
import numpy as np
import xarray as xr
import pandas as pd
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def getMERRA2stream(cdate):

    # MERRA2 streams starting dates
    d1 = datetime.strptime('19800101', '%Y%m%d').date()
    d2 = datetime.strptime('19920101', '%Y%m%d').date()
    d3 = datetime.strptime('20010101', '%Y%m%d').date()
    d4 = datetime.strptime('20110101', '%Y%m%d').date()

    today = datetime.today().date()

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

    df_avg = df.groupby([pd.Grouper(freq=str(freq)+'H', level=ind_time)] +
                        [level_values(i) for i in [ind_lat, ind_lon]]).mean()

    da_out = df_avg.to_xarray()

    da_out.lat.attrs = da_in.lat.attrs
    da_out.lon.attrs = da_in.lon.attrs
    da_out.time.attrs = da_in.time.attrs
    da_out['time'] = da_out.time.get_index('time') + timedelta(hours=freq/2)
    da_out.time.encoding['dtype'] = "double"
    da_out.time.encoding['units'] = "seconds since 1970-01-01 00:00:00"
    da_out.time.encoding['calendar'] = "standard"
    timeAttrs = ["long_name", "units", "calendar"]
    da_out.time.attrs = {key:val for key, val in da_out.time.attrs.items() if key in timeAttrs}
    da_out[da_in.name].attrs = da_in.attrs

    da_out.encoding['unlimited_dims'] = ['time']

    return da_out


def readMERRA2(fname, varname):

    if not os.path.exists(fname):
        raise FileNotFoundError(fname+' does not exist!')

    DS = xr.open_dataset(fname)
    da = DS.get(varname)
    DS.close()

    return da

def _threadedForc(args):

    fileName, varName, tAvg, outFileName = args

    forc = timeAverage(readMERRA2(fileName, varName), tAvg)
    forc.to_netcdf(path=outFileName, mode='w')

    return


if __name__ == "__main__":

    host = socket.gethostname()
    if host.startswith('discover'):
        dirMERRA2 = "/discover/nobackup/projects/gmao/merra2"
        lMERRA2 = False
    else:
        dirMERRA2 = None
        lMERRA2 = True

    description = "Fetch and create MERRA2 Forcings for MOM6"
    outdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                             '/fluxes/merra2')

    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--date', help='date to create MERRA2 forcings for MOM6', metavar='YYYYMMDD', type=str, required=True)
    parser.add_argument('--outdir', help='directory to save final forcings to (Default: %(default)s)', type=str, default=outdir, required=False)
    parser.add_argument('--MERRA2dir', help='directory containing MERRA2 dataset (Default: %(default)s)', type=str, required=lMERRA2, default=dirMERRA2)
    parser.add_argument('--tavg_rad', help='time-averaging frequency for Radiation forcings (Default: %(default)s hours)', type=int, default=24, required=False)
    parser.add_argument('--tavg_met', help='time-averaging frequency for Meteorological forcings (Default: %(default)s hours)', type=int, default=6, required=False)
    parser.add_argument('--tavg_pcp', help='time-averaging frequency for Precipitation forcings (Default: %(default)s hours)', type=int, default=24, required=False)
    parser.add_argument("--threads", default=multiprocessing.cpu_count(), type=int, help="number of threads to use (Default: %(default)s)")

    args = parser.parse_args()

    cdate = datetime.strptime(args.date, '%Y%m%d').date()
    outdir = os.path.realpath(args.outdir)
    tAvgRad = args.tavg_rad
    tAvgMet = args.tavg_met
    tAvgPcp = args.tavg_pcp
    dirMERRA2 = args.MERRA2dir
    threads = args.threads if args.threads <= 8 else 8 # Use 8 threads only, if more available

    outdir = os.path.join(outdir, '{:%Y/%Y%m%d}'.format(cdate))
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    stream = getMERRA2stream(cdate)

    pth = os.path.join(dirMERRA2, 'data/products', stream, '{:Y%Y/M%m}'.format(cdate))

    rad = os.path.join(pth, stream+'.tavg1_2d_rad_Nx.{:%Y%m%d}.nc4'.format(cdate))
    asm = os.path.join(pth, stream+'.inst1_2d_asm_Nx.{:%Y%m%d}.nc4'.format(cdate))
    flx = os.path.join(pth, stream+'.tavg1_2d_flx_Nx.{:%Y%m%d}.nc4'.format(cdate))

    # MERRA2 variables to create forcings from and their attributes
    merra2Dict = {
        "SWGNT"   : {'readFrom': rad, 'tAvg': tAvgRad},
        "LWGNT"   : {'readFrom': rad, 'tAvg': tAvgRad},
        "SLP"     : {'readFrom': asm, 'tAvg': tAvgMet},
        "U10M"    : {'readFrom': asm, 'tAvg': tAvgMet},
        "V10M"    : {'readFrom': asm, 'tAvg': tAvgMet},
        "T2M"     : {'readFrom': asm, 'tAvg': tAvgMet},
        "QV2M"    : {'readFrom': asm, 'tAvg': tAvgMet},
        "PRECTOT" : {'readFrom': flx, 'tAvg': tAvgPcp}
    }

    # Prepare to thread the forcing maker
    paramIn = []
    for varName, varDict in merra2Dict.items():
        fileName = varDict['readFrom']
        tAvg = varDict['tAvg']
        outFileName = os.path.join(outdir, 'merra2.{:%Y%m%d}.{}.nc4'.format(cdate, varName))
        paramIn.append((fileName, varName, tAvg, outFileName))

    # Thread the forcing maker
    pool = multiprocessing.Pool(threads)
    pool.map(_threadedForc, paramIn)

    sys.exit(0)
