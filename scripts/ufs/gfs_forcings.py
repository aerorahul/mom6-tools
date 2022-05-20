#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from typing import Union
import numpy as np
import xarray as xr
import logging

# Set global logger
LEVEL = 'INFO'
FORMAT = '%(asctime)s - %(levelname)-8s - %(name)-8s: %(message)s'
logging.basicConfig(level=LEVEL, format=FORMAT)
logger = logging.getLogger('forcing')

# Variables to read from sfcf000 and sfcf006 files:
SFCF000_VARS = ['lon', 'lat', 'time',
                'ulwrf', 'dlwrf', 'dswrf',
                'vbdsf_ave', 'vddsf_ave', 'nbdsf_ave', 'nddsf_ave',
                'pressfc', 'tmp2m', 'spfh2m', 'ugrd10m', 'vgrd10m',
                'hgt_hyblev1', 'tmp_hyblev1', 'spfh_hyblev1',
                'ugrd_hyblev1', 'vgrd_hyblev1',
                'land',
                'shtfl_ave', 'lhtfl_ave', 'icec']
SFCF006_VARS = ['uflx_ave', 'vflx_ave', 'prate_ave']


def read_dataset(filename: Path, variables: Union[str, list]) -> xr.Dataset:
    """
    Lazy-read variables from a file into an xarray.Dataset
    """

    logger.info(f'reading file: {filename}')
    logger.debug(f"reading variables: {', '.join(variables)}")
    with xr.open_dataset(filename) as ds:
        da = ds.get(variables)

    return da


def get_coeff(temp: xr.DataArray, threshold: float = -15.) -> xr.DataArray:
    """
    Generate a coefficient mask based on temperature and a threshold
    """

    temp_celcius = temp - 273.15  # Freezing point 273.15F

    # mix of rain and snow based on temp
    coeff = (threshold - temp_celcius) / threshold
    coeff = xr.where(temp_celcius >= 0., 1., coeff)  # all rain
    coeff = xr.where(temp_celcius < threshold, 0., coeff)  # all snow

    return coeff


def compute_pressure(pressfc: xr.DataArray,
                     height: xr.DataArray,
                     temp: xr.DataArray) -> xr.DataArray:
    """
    Compute pressure from pressure equation
    """

    gravity = 9.80665  # gravity (m/s2)
    Rd = 287.058  # gas constant for dry air (J/K/kg)

    pressure = pressfc * np.exp(-gravity * height/(Rd*temp))
    pressure.attrs = pressfc.attrs
    pressure.attrs['long_name'] = 'layer 1 pressure'

    return pressure


def input_args():

    description = """
    Read ufs-weather-model produced surface files to
    generate atmospheric forcings for use with the
    CDEPS component of the ufs-weather-model
    """
    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--sfcf000', type=str, default='sfcf000.nc',
                        required=True,
                        help='sfcf000.nc at the current cycle time')
    parser.add_argument('--sfcf006', type=str, default='sfcf006.nc',
                        required=True,
                        help='sfcf006.nc at the current cycle time initialized 6hours ago')
    parser.add_argument('--forcing', type=str, default='forcing.nc',
                        required=False,
                        help='output file containing atmospheric forcings')
    parser.add_argument('--debug', action='store_true',
                        required=False,
                        help='print debugging statements')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(level='DEBUG')

    return args


if __name__ == '__main__':

    logger.info(f'starting ...')

    # Gather user inputs
    user_inputs = input_args()

    # Read files into dataset
    dsfcf000 = read_dataset(user_inputs.sfcf000, SFCF000_VARS)
    dsfcf006 = read_dataset(user_inputs.sfcf006, SFCF006_VARS)

    # Create forcing dataset
    dforcing = xr.merge([dsfcf000, dsfcf006])

    # Drop variables not required in the forcing dataset
    dforcing = dforcing.drop_vars(['prate_ave'])
    #  Also drop irrelevant global attributes
    for attr in ['fhzero', 'ncld', 'nsoil', 'imp_physics', 'dtp']:
        dforcing.attrs.pop(attr)

    # Replace the following with these scaled variants
    for varName in ['vbdsf_ave', 'vddsf_ave']:
        dforcing[varName] = dsfcf000['dswrf'] * 0.285
        dforcing[varName].attrs = dsfcf000[varName].attrs

    for varName in ['nbdsf_ave', 'nddsf_ave']:
        dforcing[varName] = dsfcf000['dswrf'] * 0.215
        dforcing[varName].attrs = dsfcf000[varName].attrs

    # Collect precipitation rates from prate_ave
    coeff = get_coeff(dsfcf000['tmp2m'], threshold=-15.)
    dforcing['precp'] = coeff * dsfcf006['prate_ave']
    dforcing['precp'].attrs = dsfcf006['prate_ave'].attrs
    dforcing['precp'].attrs['long_name'] = 'surface rain precipitation rate'
    dforcing['fprecp'] = (1.0 - coeff) * dsfcf006['prate_ave']
    dforcing['fprecp'].attrs = dsfcf006['prate_ave'].attrs
    dforcing['fprecp'].attrs['long_name'] = 'surface snow precipitation rate'

    # Compute layer 1 pressure
    dforcing['pres_hyblev1'] = compute_pressure(
        dsfcf000['pressfc'], dsfcf000['hgt_hyblev1'], dsfcf000['tmp_hyblev1'])

    # Write forcing dataset to file
    logger.info(f'writing file: {user_inputs.forcing}')
    dforcing.to_netcdf(user_inputs.forcing)

    logger.info(f'done!')
