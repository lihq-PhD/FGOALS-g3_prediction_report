import sys
import numpy as np
import pandas as pd
import xarray as xr
import salem

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmaps 
import matplotlib
import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.util import add_cyclic_point

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CAL_NINO:
    def __init__(self, current_yr=sys.argv[1], current_mon=sys.argv[2]):
        self.model_mme_path = './tmp/atm3D_MME.nc'
        self.current_yr = int(current_yr)
        self.current_mon = int(current_mon)
        self.current_date = datetime(self.current_yr, self.current_mon, 1)
        self.start_date = self.current_date - relativedelta(months=6)
        self.end_date = self.current_date + relativedelta(months=12)

    def atm(self, ):
        model_mme_prec = xr.open_dataset(self.model_mme_path)['PRECT']
        model_mme_prec = model_mme_prec.loc[self.current_date:self.end_date]
        model_mme_prec = model_mme_prec.sel(lat=slice(-70, 70)) * 86400000

        model_mme_temp = xr.open_dataset(self.model_mme_path)['ts']
        model_mme_temp = model_mme_temp.loc[self.current_date:self.end_date]
        model_mme_temp = model_mme_temp.sel(lat=slice(-70, 70)) 

        # 1-3
        model_mme_prec_1_3 = model_mme_prec[0:3, ...].mean(dim=['time'])
        model_mme_temp_1_3 = model_mme_temp[0:3, ...].mean(dim=['time'])
        # 4-6
        model_mme_prec_4_6 = model_mme_prec[3:6, ...].mean(dim=['time'])
        model_mme_temp_4_6 = model_mme_temp[3:6, ...].mean(dim=['time'])
        # 7-9
        model_mme_prec_7_9 = model_mme_prec[6:9, ...].mean(dim=['time'])
        model_mme_temp_7_9 = model_mme_temp[6:9, ...].mean(dim=['time'])
        # 10-12
        model_mme_prec_10_12 = model_mme_prec[9:12, ...].mean(dim=['time'])
        model_mme_temp_10_12 = model_mme_temp[9:12, ...].mean(dim=['time'])
        return [model_mme_prec_1_3, model_mme_prec_4_6, model_mme_prec_7_9, model_mme_prec_10_12], \
                [model_mme_temp_1_3, model_mme_temp_4_6, model_mme_temp_7_9, model_mme_temp_10_12]
    
def plt_share1(ax):
    ax.set_extent([0, 360, -70, 70], crs=ccrs.PlateCarree())
    ax.set_aspect(1.2)

    ax.add_feature(cfeature.LAND, ls='-', ec='k', fc='w', lw=0.2, zorder=2)
    ax.set_xticks(np.arange(0, 361, 60), crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(0, 361, 20), minor=True, crs=ccrs.PlateCarree())
    ax.set_xticklabels(['0°', '60°E', '120°E', '180°', '120°W', '60°W', '0°'], fontsize=8)
    ax.set_yticks(np.arange(-60, 61, 30), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-60, 61, 15), minor=True, crs=ccrs.PlateCarree())
    ax.set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N'], fontsize=8)

    ax.tick_params(axis='both', width=0.5, length=3)
    ax.tick_params(axis='both', width=0.5, length=1.5, which='minor')
    for spi in ['top', 'bottom', 'left', 'right']:
        ax.spines[spi].set_visible(True)
        ax.spines[spi].set_linewidth(0.5)
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5)
    return ax

def plt_share2(ax):
    ax.set_extent([-180, 180, -70, 70], crs=ccrs.PlateCarree())
    ax.set_aspect(1.2)

    ax.add_feature(cfeature.LAND, ls='-', ec='k', fc='None', lw=0.2, zorder=2)
    ax.set_xticks(np.arange(-180, 181, 60), crs=ccrs.PlateCarree())
    ax.set_xticks(np.arange(-180, 181, 20), minor=True, crs=ccrs.PlateCarree())
    ax.set_xticklabels(['180°', '120°W', '60°W', '0°', '60°E', '120°E', '180°'], fontsize=8)
    ax.set_yticks(np.arange(-60, 61, 30), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(-60, 61, 15), minor=True, crs=ccrs.PlateCarree())
    ax.set_yticklabels(['60°S', '30°S', '0°', '30°N', '60°N'], fontsize=8)

    ax.tick_params(axis='both', width=0.5, length=3)
    ax.tick_params(axis='both', width=0.5, length=1.5, which='minor')
    for spi in ['top', 'bottom', 'left', 'right']:
        ax.spines[spi].set_visible(True)
        ax.spines[spi].set_linewidth(0.5)
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5)
    return ax


if __name__ == "__main__":
    cal_nino = CAL_NINO()

    model_prec, model_temp = cal_nino.atm()
    lon, lat = model_prec[0]['lon'], model_prec[0]['lat']

    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=200)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()
    geo_dict = {
        'levels': np.arange(-2.0, 2.01, 0.2),
        'cmap': cmaps.precip4_diff_19lev,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share1(ax)
        data, cycle_lon = add_cyclic_point(model_prec[n], coord=lon)
        dplot = ax.contourf(cycle_lon, lat, data, **geo_dict)
        ax.set_title('Precip. {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-2.0, 2.01, 0.4))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/precip_ocean_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
    plt.close()

    # land precip
    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()
    geo_dict = {
        'levels': np.arange(-1.0, 1.01, 0.1),
        'cmap': cmaps.precip4_diff_19lev,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share2(ax)
        shp = salem.read_shapefile('./plot/land/ne_110m_land.shp')
        data = model_prec[n].assign_coords(lon=(((model_prec[n].lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax.contourf(data.lon, lat, masked_data, **geo_dict)
        ax.set_title('Precip. {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-1.0, 1.01, 0.2))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/precip_land_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
    plt.close()




    # land temp
    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=0)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()
    geo_dict = {
        'levels': np.arange(-2.0, 2.01, 0.2),
        'cmap': cmaps.temp_19lev,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share2(ax)
        shp = salem.read_shapefile('./plot/land/ne_110m_land.shp')
        data = model_temp[n].assign_coords(lon=(((model_temp[n].lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax.contourf(data.lon, lat, masked_data, **geo_dict)
        ax.set_title('Temp. {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-2.0, 2.01, 0.4))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/temp_land_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
    plt.close()