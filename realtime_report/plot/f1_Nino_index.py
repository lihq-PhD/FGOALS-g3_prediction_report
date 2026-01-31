import sys
import numpy as np
import pandas as pd
import xarray as xr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmaps 
import matplotlib
import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CAL_NINO:
    def __init__(self, current_yr=sys.argv[1], current_mon=sys.argv[2]):
        self.obs_path = './tmp/HadISST_ssta_1x1.nc'
        self.model_mme_path = './tmp/thetao_MME.nc'
        self.model_members_path = ['./tmp/thetao_F01_00_C0100.nc', './tmp/thetao_F01_00_C0200.nc', './tmp/thetao_F02_00_C0100.nc', './tmp/thetao_F02_00_C0200.nc',
                                   './tmp/thetao_A01_00_C0100.nc', './tmp/thetao_A01_00_C0200.nc', './tmp/thetao_A02_00_C0100.nc', './tmp/thetao_A02_00_C0200.nc',]
        self.current_yr = int(current_yr)
        self.current_mon = int(current_mon)
        self.current_date = datetime(self.current_yr, self.current_mon, 1)
        self.start_date = self.current_date - relativedelta(months=6)
        self.end_date = self.current_date + relativedelta(months=12)

    def nino34(self, lat, lon):
        obs_ssta = xr.open_dataset(self.obs_path)['sst']
        obs_ssta = obs_ssta.loc[self.start_date:self.current_date][:-1, ...]
        obs_nino34 = obs_ssta.sel(lat=lat, lon=lon).mean(dim=['lat', 'lon'])

        model_mme_ssta = xr.open_dataset(self.model_mme_path)['thetao']
        model_mme_nino34 = model_mme_ssta.sel(lev=5, lat=lat, lon=lon).mean(dim=['lat', 'lon'])

        model_members_nino34 = []
        for m in self.model_members_path:
            model_ssta = xr.open_dataset(m)['thetao']
            model_nino34 = model_ssta.sel(lev=5, lat=lat, lon=lon).mean(dim=['lat', 'lon'])
            model_members_nino34.append(model_nino34)
        return obs_nino34, model_mme_nino34, model_members_nino34
    
def plt_share(ax):
    ax.set_aspect(21/7/1.6)
    ax.set_xlim((0, 21))
    ax.set_ylim((-3.5, 3.5))

    ax.set_xticks(np.arange(1, 19.1, 3))
    ax.set_xticks(np.arange(1, 19.1, 1), minor=True)
    # ax.set_xticklabels([1, 4, 7, 10, 13], fontsize=6)
    ax.set_yticks(np.arange(-3.0, 3.01, 1.0))
    ax.set_yticks(np.arange(-3.5, 3.51, 0.5), minor=True)
    ax.set_yticklabels([-3, -2, -1, 0, 1, 2, 3], fontsize=8)

    ax.tick_params(axis='x', width=0.6, length=4)
    ax.tick_params(axis='y', width=0.6, length=4)
    ax.tick_params(axis='x', width=0.6, length=2.5, which='minor')
    ax.tick_params(axis='y', width=0.6, length=2.5, which='minor')
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5, axis='y')
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5, axis='x')

    ax.axhline(y=0.0, ls='--', c='k', lw=0.3)

    for spi in ['bottom', 'left', 'top', 'right']:
        ax.spines[spi].set_visible(True)
        ax.spines[spi].set_linewidth(0.6)
    return ax



if __name__ == "__main__":
    cal_nino = CAL_NINO()
    
    obs_nino34, model_mme_nino34, model_members_nino34 = cal_nino.nino34(lat=slice(-5, 5), lon=slice(190, 240))
    obs_nino3, model_mme_nino3, model_members_nino3 = cal_nino.nino34(lat=slice(-5, 5), lon=slice(210, 270))
    obs_nino4, model_mme_nino4, model_members_nino4 = cal_nino.nino34(lat=slice(-5, 5), lon=slice(160, 210))
    obs_nino12, model_mme_nino12, model_members_nino12 = cal_nino.nino34(lat=slice(-10, 0), lon=slice(270, 280))

    # nino34
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('Niño3.4 index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_nino34, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino34[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino34[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_nino34[-1], model_mme_nino34[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_nino34, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_nino34.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/nino34_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # nino3
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('Niño3 index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_nino3, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino3[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino3[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_nino3[-1], model_mme_nino3[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_nino3, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_nino3.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/nino3_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # nino4
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('Niño4 index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_nino4, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino4[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino4[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_nino4[-1], model_mme_nino4[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_nino4, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_nino4.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/nino4_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # nino12
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('Niño1+2 index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_nino12, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino12[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_nino12[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_nino12[-1], model_mme_nino12[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_nino12, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_nino12.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/nino12_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')