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

    def EMI(self):
        obs_ssta = xr.open_dataset(self.obs_path)['sst']
        obs_ssta = obs_ssta.loc[self.start_date:self.current_date][:-1, ...]
        a = obs_ssta.sel(lat=slice(-10, 10), lon=slice(165, 220)).mean(dim=['lat', 'lon'])
        b = obs_ssta.sel(lat=slice(-15, 5), lon=slice(250, 290)).mean(dim=['lat', 'lon'])
        c = obs_ssta.sel(lat=slice(-10, 20), lon=slice(125, 145)).mean(dim=['lat', 'lon'])
        obs_emi = a - (b + c) / 2

        model_mme_ssta = xr.open_dataset(self.model_mme_path)['thetao']
        a = model_mme_ssta.sel(lev=5, lat=slice(-10, 10), lon=slice(165, 220)).mean(dim=['lat', 'lon'])
        b = model_mme_ssta.sel(lev=5, lat=slice(-15, 5), lon=slice(250, 290)).mean(dim=['lat', 'lon'])
        c = model_mme_ssta.sel(lev=5, lat=slice(-10, 20), lon=slice(125, 145)).mean(dim=['lat', 'lon'])
        model_mme_emi = a - (b + c) / 2

        model_members_emi = []
        for m in self.model_members_path:
            model_ssta = xr.open_dataset(m)['thetao']
            a = model_ssta.sel(lev=5, lat=slice(-10, 10), lon=slice(165, 220)).mean(dim=['lat', 'lon'])
            b = model_ssta.sel(lev=5, lat=slice(-15, 5), lon=slice(250, 290)).mean(dim=['lat', 'lon'])
            c = model_ssta.sel(lev=5, lat=slice(-10, 20), lon=slice(125, 145)).mean(dim=['lat', 'lon'])
            model_emi = a - (b + c) / 2
            model_members_emi.append(model_emi)
        return obs_emi, model_mme_emi, model_members_emi
    
    def WIO(self):
        obs_ssta = xr.open_dataset(self.obs_path)['sst']
        obs_ssta = obs_ssta.loc[self.start_date:self.current_date][:-1, ...]
        obs_wio = obs_ssta.sel(lat=slice(-10, 10), lon=slice(50, 70)).mean(dim=['lat', 'lon'])

        model_mme_ssta = xr.open_dataset(self.model_mme_path)['thetao']
        model_mme_wio = model_mme_ssta.sel(lev=5, lat=slice(-10, 10), lon=slice(50, 70)).mean(dim=['lat', 'lon'])

        model_members_wio = []
        for m in self.model_members_path:
            model_ssta = xr.open_dataset(m)['thetao']
            model_wio = model_ssta.sel(lev=5, lat=slice(-10, 10), lon=slice(50, 70)).mean(dim=['lat', 'lon'])
            model_members_wio.append(model_wio)
        return obs_wio, model_mme_wio, model_members_wio

    def EIO(self):
        obs_ssta = xr.open_dataset(self.obs_path)['sst']
        obs_ssta = obs_ssta.loc[self.start_date:self.current_date][:-1, ...]
        obs_eio = obs_ssta.sel(lat=slice(-10, 0), lon=slice(90, 110)).mean(dim=['lat', 'lon'])

        model_mme_ssta = xr.open_dataset(self.model_mme_path)['thetao']
        model_mme_eio = model_mme_ssta.sel(lev=5, lat=slice(-10, 0), lon=slice(90, 110)).mean(dim=['lat', 'lon'])

        model_members_eio = []
        for m in self.model_members_path:
            model_ssta = xr.open_dataset(m)['thetao']
            model_eio = model_ssta.sel(lev=5, lat=slice(-10, 0), lon=slice(90, 110)).mean(dim=['lat', 'lon'])
            model_members_eio.append(model_eio)
        return obs_eio, model_mme_eio, model_members_eio

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

    obs_emi, model_mme_emi, model_members_emi = cal_nino.EMI()
    obs_wio, model_mme_wio, model_members_wio = cal_nino.WIO()
    obs_eio, model_mme_eio, model_members_eio = cal_nino.EIO()

    # emi
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('EMI index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_emi, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_emi[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_emi[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_emi[-1], model_mme_emi[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_emi, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_emi.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/emi_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # wio
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('WIO index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_wio, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_wio[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_wio[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_wio[-1], model_mme_wio[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_wio, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_wio.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/wio_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # eio
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('EIO index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_eio, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_eio[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_eio[m], c='grey', lw=0.8)
    
    ax.plot([6, 7], [obs_eio[-1], model_mme_eio[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_eio, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)
    
    if obs_eio.mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/eio_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    # dmi
    fig, ax = plt.subplots(1, 1, figsize=(12/2.54, 10/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_xticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='right', fontweight='bold')
    ax.set_title('Dipole mode index', fontsize=10, loc='left', fontweight='bold')

    ax.plot(np.arange(1, 6.1, 1), obs_wio - obs_eio, c='k', lw=1.0, label='OBS')
    for m in range(8):
        if m == 0:
            ax.plot(np.arange(7, 19.1, 1), model_members_wio[m] - model_members_eio[m], c='grey', lw=0.8, label='8 members')
        else:
            ax.plot(np.arange(7, 19.1, 1), model_members_wio[m] - model_members_eio[m], c='grey', lw=0.8)

    ax.plot([6, 7], [obs_wio[-1] - obs_eio[-1], model_mme_wio[0] - model_mme_eio[0]], c='k', lw=1.0, ls='--')
    ax.plot(np.arange(7, 19.1, 1), model_mme_wio - model_mme_eio, c='r', lw=1.5, label='FGOALS-g3 (MME)', marker='o', markersize=3, markerfacecolor='w', markeredgewidth=1.0)

    if (obs_wio - obs_eio).mean() >= 0:
        ax.legend(ncol=1, frameon=False, loc='lower left', fontsize=8)
    else:
        ax.legend(ncol=1, frameon=False, loc='upper left', fontsize=8)
    plt.savefig('./pic/dmi_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
