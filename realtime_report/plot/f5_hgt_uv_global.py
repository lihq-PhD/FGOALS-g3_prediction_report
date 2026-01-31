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
from cartopy.util import add_cyclic_point

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CAL_NINO:
    def __init__(self, current_yr=sys.argv[1], current_mon=sys.argv[2]):
        self.model_mme_path = './tmp/atm4D_MME.nc'
        self.current_yr = int(current_yr)
        self.current_mon = int(current_mon)
        self.current_date = datetime(self.current_yr, self.current_mon, 1)
        self.start_date = self.current_date - relativedelta(months=6)
        self.end_date = self.current_date + relativedelta(months=12)

    def atm(self, lev):
        model_mme_hgt = xr.open_dataset(self.model_mme_path)['hgt']
        model_mme_hgt = model_mme_hgt.loc[self.current_date:self.end_date]
        model_mme_hgt = model_mme_hgt.sel(lev=lev, lat=slice(-70, 70))

        model_mme_u = xr.open_dataset(self.model_mme_path)['U']
        model_mme_u = model_mme_u.loc[self.current_date:self.end_date]
        model_mme_u = model_mme_u.sel(lev=lev, lat=slice(-70, 70))

        model_mme_v = xr.open_dataset(self.model_mme_path)['V']
        model_mme_v = model_mme_v.loc[self.current_date:self.end_date]
        model_mme_v = model_mme_v.sel(lev=lev, lat=slice(-70, 70))

        # 1-3
        model_mme_hgt_1_3 = model_mme_hgt[0:3, ...].mean(dim=['time'])
        model_mme_u_1_3 = model_mme_u[0:3, ...].mean(dim=['time'])
        model_mme_v_1_3 = model_mme_v[0:3, ...].mean(dim=['time'])
        # 4-6
        model_mme_hgt_4_6 = model_mme_hgt[3:6, ...].mean(dim=['time'])
        model_mme_u_4_6 = model_mme_u[3:6, ...].mean(dim=['time'])
        model_mme_v_4_6 = model_mme_v[3:6, ...].mean(dim=['time'])
        # 7-9
        model_mme_hgt_7_9 = model_mme_hgt[6:9, ...].mean(dim=['time'])
        model_mme_u_7_9 = model_mme_u[6:9, ...].mean(dim=['time'])
        model_mme_v_7_9 = model_mme_v[6:9, ...].mean(dim=['time'])
        # 10-12
        model_mme_hgt_10_12 = model_mme_hgt[9:12, ...].mean(dim=['time'])
        model_mme_u_10_12 = model_mme_u[9:12, ...].mean(dim=['time'])
        model_mme_v_10_12 = model_mme_v[9:12, ...].mean(dim=['time'])
        return [model_mme_hgt_1_3, model_mme_hgt_4_6, model_mme_hgt_7_9, model_mme_hgt_10_12],\
                [model_mme_u_1_3, model_mme_u_4_6, model_mme_u_7_9, model_mme_u_10_12],\
                [model_mme_v_1_3, model_mme_v_4_6, model_mme_v_7_9, model_mme_v_10_12]
    
def plt_share(ax):
    ax.set_extent([0, 360, -70, 70], crs=ccrs.PlateCarree())
    ax.set_aspect(1.2)

    ax.add_feature(cfeature.LAND, ls='-', ec='k', fc='None', lw=0.2, zorder=2)
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

if __name__ == "__main__":
    cal_nino = CAL_NINO()

    model_hgt_850, model_u_850, model_v_850 = cal_nino.atm(lev=850)
    model_hgt_500, model_u_500, model_v_500 = cal_nino.atm(lev=500)
    model_hgt_200, model_u_200, model_v_200 = cal_nino.atm(lev=200)
    lon, lat = model_hgt_850[0]['lon'], model_hgt_850[0]['lat']

    geo_dict = {
        'levels': np.arange(-30.0, 30.1, 3),
        'cmap': cmaps.cmp_flux,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    quiver_color = {
        'width': 0.001, 
        'headwidth': 10.5, 
        'headaxislength': 4, 
        'scale': 25,
        'pivot': 'mid', 
        'color': 'k', 
        'zorder': 3, 
        'transform': ccrs.PlateCarree(),
    }
    quiverkey_color = {
        'X': 0.80, 
        'Y': -0.3, 
        'U': 1, 
        'angle': 0, 
        'label': '1 m/s', 
        'labelpos': 'E', 
        'color': 'k', 
        'labelcolor': 'k', 
        'fontproperties': {'size': 9},
    }

    # 850
    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=200)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()

    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share(ax)
        data, cycle_lon = add_cyclic_point(model_hgt_850[n], coord=lon)
        dplot = ax.contourf(cycle_lon, lat, data, **geo_dict)
        ax.set_title('HGT&UV850 {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

        shp = Reader('./plot/Tibet/Tibet.shp')
        ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='None', linewidth=0.2)

        u, cycle_lon = add_cyclic_point(model_u_850[n], coord=lon)
        v, cycle_lon = add_cyclic_point(model_v_850[n], coord=lon)
        dplot0 = ax.quiver(cycle_lon[::6], lat[::4], u[::4, ::6], v[::4, ::6], **quiver_color)
    ax.quiverkey(dplot0, **quiverkey_color)

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-30.0, 30.1, 6))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/hgtuv850_global_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    quiver_color = {
        'width': 0.001, 
        'headwidth': 10.5, 
        'headaxislength': 4, 
        'scale': 45,
        'pivot': 'mid', 
        'color': 'k', 
        'zorder': 3, 
        'transform': ccrs.PlateCarree(),
    }
    quiverkey_color = {
        'X': 0.80, 
        'Y': -0.3, 
        'U': 2, 
        'angle': 0, 
        'label': '2 m/s', 
        'labelpos': 'E', 
        'color': 'k', 
        'labelcolor': 'k', 
        'fontproperties': {'size': 9},
    }
    # 500
    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=200)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()

    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share(ax)
        data, cycle_lon = add_cyclic_point(model_hgt_500[n], coord=lon)
        dplot = ax.contourf(cycle_lon, lat, data, **geo_dict)
        ax.set_title('HGT&UV500 {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

        shp = Reader('./plot/Tibet/Tibet.shp')
        ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='None', linewidth=0.2)

        u, cycle_lon = add_cyclic_point(model_u_500[n], coord=lon)
        v, cycle_lon = add_cyclic_point(model_v_500[n], coord=lon)
        dplot0 = ax.quiver(cycle_lon[::6], lat[::4], u[::4, ::6], v[::4, ::6], **quiver_color)
    ax.quiverkey(dplot0, **quiverkey_color)

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-30.0, 30.1, 6))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/hgtuv500_global_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')

    geo_dict = {
        'levels': np.arange(-40.0, 40.1, 4),
        'cmap': cmaps.cmp_flux,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    quiver_color = {
        'width': 0.001, 
        'headwidth': 10.5, 
        'headaxislength': 4, 
        'scale': 65,
        'pivot': 'mid', 
        'color': 'k', 
        'zorder': 3, 
        'transform': ccrs.PlateCarree(),
    }
    quiverkey_color = {
        'X': 0.80, 
        'Y': -0.3, 
        'U': 3, 
        'angle': 0, 
        'label': '3 m/s', 
        'labelpos': 'E', 
        'color': 'k', 
        'labelcolor': 'k', 
        'fontproperties': {'size': 9},
    }
    # 200
    fig, axes = plt.subplots(2, 2, figsize=(18/2.54, 12/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=200)})
    fig.tight_layout(w_pad=4.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()

    for n in range(4):
        ax = axes.flat[n]
        ax = plt_share(ax)
        data, cycle_lon = add_cyclic_point(model_hgt_200[n], coord=lon)
        dplot = ax.contourf(cycle_lon, lat, data, **geo_dict)
        ax.set_title('HGT&UV200 {}-{} forecast'.format(labels[n*3], labels[n*3+2]), fontsize=10, loc='left', fontweight='bold')

        shp = Reader('./plot/Tibet/Tibet.shp')
        ax.add_geometries(shp.geometries(), ccrs.PlateCarree(), edgecolor='grey', facecolor='None', linewidth=0.2)

        u, cycle_lon = add_cyclic_point(model_u_200[n], coord=lon)
        v, cycle_lon = add_cyclic_point(model_v_200[n], coord=lon)
        dplot0 = ax.quiver(cycle_lon[::6], lat[::4], u[::4, ::6], v[::4, ::6], **quiver_color)
    ax.quiverkey(dplot0, **quiverkey_color)

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-40.0, 40.1, 8))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/hgtuv200_global_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')