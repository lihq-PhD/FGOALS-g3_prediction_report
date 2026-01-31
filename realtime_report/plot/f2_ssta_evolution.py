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
    
    def ssta(self, ):
        obs_ssta = xr.open_dataset(self.obs_path)['sst']
        obs_ssta = obs_ssta.loc[self.start_date:self.current_date][:-1, ...]
        obs_ssta = obs_ssta.sel(lat=slice(-5, 5), lon=slice(120, 280)).mean(dim=['lat'])

        model_mme_ssta = xr.open_dataset(self.model_mme_path)['thetao']
        model_mme_ssta = model_mme_ssta.sel(lev=5, lat=slice(-5, 5), lon=slice(120, 280)).mean(dim=['lat'])
        return obs_ssta, model_mme_ssta

def plt_share(ax):
    ax.set_aspect(160/18/0.6)
    ax.set_xlim((120, 280))
    ax.set_ylim((1, 19))

    ax.set_xticks(np.arange(120, 280.1, 40))
    ax.set_xticks(np.arange(120, 280.1, 20), minor=True)
    ax.set_xticklabels(['120°E', '160°E', '160°W', '120°W', '80°W'], fontsize=8)
    ax.set_yticks(np.arange(1.0, 19.1, 3.0))
    ax.set_yticks(np.arange(1.0, 19.1, 1.0), minor=True)
    # ax.set_yticklabels([-3, -2, -1, 0, 1, 2, 3], fontsize=8)

    ax.tick_params(axis='x', width=0.6, length=4)
    ax.tick_params(axis='y', width=0.6, length=4)
    ax.tick_params(axis='x', width=0.6, length=2.5, which='minor')
    ax.tick_params(axis='y', width=0.6, length=2.5, which='minor')
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5, axis='y')
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5, axis='x')

    ax.axhline(y=7.0, ls='-', c='k', lw=0.6)

    for spi in ['bottom', 'left', 'top', 'right']:
        ax.spines[spi].set_visible(True)
        ax.spines[spi].set_linewidth(0.6)
    return ax

if __name__ == "__main__":
    cal_nino = CAL_NINO()

    obs_ssta, model_mme_ssta = cal_nino.ssta()
    lon = obs_ssta['lon']
    combined = np.concatenate([obs_ssta, model_mme_ssta], axis=0)

    fig, ax = plt.subplots(1, 1, figsize=(10/2.54, 12/2.54))
    ax = plt_share(ax)
    labels = pd.date_range(start=cal_nino.start_date.strftime('%Y-%m'), periods=19, freq='MS').strftime('%Y%m').tolist()
    ax.set_yticklabels(labels[::3], fontsize=8)
    ax.set_title('Pred. from {}-{}'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), fontsize=10, loc='left', fontweight='bold')

    dplot = ax.contourf(lon, np.arange(1, 19.1, 1), combined, levels=np.arange(-3.6, 3.61, 0.3), cmap=cmaps.ncl_default, extend='both')
    ax.contour(lon, np.arange(1, 19.1, 1), combined, levels=np.arange(-3.6, 3.61, 0.6), colors='k', linewidths=0.5)

    ax.text(125, 6, 'OBS', fontsize=8)
    ax.text(125, 7.5, 'FGOALS-g3', fontsize=8)

    cbar_color = {
        'orientation': 'vertical', 
        'shrink': 0.7, 
        'pad': 0.05, 
        'fraction': 0.05, 
        'aspect': 40,
    }
    cbar = plt.colorbar(dplot, ax=ax, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-3.6, 3.61, 0.6))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)

    plt.savefig('./pic/ssta_evolution_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
