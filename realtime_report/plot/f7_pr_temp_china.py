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

    def interp(self, data_array):
        lat_min, lat_max = 10, 60
        lon_min, lon_max = 70, 140
        
        lat_points = int((lat_max - lat_min) / 0.25) + 1
        lon_points = int((lon_max - lon_min) / 0.25) + 1
        
        target_lat = np.linspace(lat_min, lat_max, lat_points)
        target_lon = np.linspace(lon_min, lon_max, lon_points)

        interpolated = data_array.interp(
            lat=target_lat,
            lon=target_lon,
            method='linear', 
            kwargs={"fill_value": "extrapolate"}
        )
        return interpolated

    def atm(self, ):
        model_mme_prec = xr.open_dataset(self.model_mme_path)['PRECT']
        model_mme_prec = model_mme_prec.loc[self.current_date:self.end_date]
        model_mme_prec = model_mme_prec.sel(lat=slice(10, 60), lon=slice(70, 140)) * 86400000
        model_mme_prec = self.interp(model_mme_prec)

        model_mme_prec_small = xr.open_dataset(self.model_mme_path)['PRECT']
        model_mme_prec_small = model_mme_prec_small.loc[self.current_date:self.end_date]
        model_mme_prec_small = model_mme_prec_small.sel(lat=slice(0, 25), lon=slice(104, 125)) * 86400000
        model_mme_prec_small = self.interp(model_mme_prec_small)

        model_mme_temp = xr.open_dataset(self.model_mme_path)['ts']
        model_mme_temp = model_mme_temp.loc[self.current_date:self.end_date]
        model_mme_temp = model_mme_temp.sel(lat=slice(10, 60), lon=slice(70, 140)) 
        model_mme_temp = self.interp(model_mme_temp)

        model_mme_temp_small = xr.open_dataset(self.model_mme_path)['ts']
        model_mme_temp_small = model_mme_temp_small.loc[self.current_date:self.end_date]
        model_mme_temp_small = model_mme_temp_small.sel(lat=slice(0, 25), lon=slice(104, 125))
        model_mme_temp_small = self.interp(model_mme_temp_small)

        # 1
        model_mme_prec_1 = model_mme_prec[0, ...]
        model_mme_prec_1_small = model_mme_prec_small[0, ...]
        model_mme_temp_1 = model_mme_temp[0, ...]
        model_mme_temp_1_small = model_mme_temp_small[0, ...]
        # 2
        model_mme_prec_2 = model_mme_prec[1, ...]
        model_mme_prec_2_small = model_mme_prec_small[1, ...]
        model_mme_temp_2 = model_mme_temp[1, ...]
        model_mme_temp_2_small = model_mme_temp_small[1, ...]
        # 3
        model_mme_prec_3 = model_mme_prec[2, ...]
        model_mme_prec_3_small = model_mme_prec_small[2, ...]
        model_mme_temp_3 = model_mme_temp[2, ...]
        model_mme_temp_3_small = model_mme_temp_small[2, ...]
        return [model_mme_prec_1, model_mme_prec_2, model_mme_prec_3], \
                [model_mme_temp_1, model_mme_temp_2, model_mme_temp_3], \
                [model_mme_prec_1_small, model_mme_prec_2_small, model_mme_prec_3_small], \
                [model_mme_temp_1_small, model_mme_temp_2_small, model_mme_temp_3_small]
    
def plt_share(ax):
    ax.set_extent([70, 140, 10, 60], crs=ccrs.PlateCarree())
    ax.set_aspect(1.2)

    ax.add_feature(cfeature.LAND, ls='-', ec='k', fc='None', lw=0.2, zorder=2)
    # ax.add_geometries(Reader('./plot/china/china.shp').geometries(), ccrs.PlateCarree(), ls='-', ec='k', fc='None', lw=0.2, zorder=3)
    ax.add_geometries(Reader('./plot/china/cnhimap.shp').geometries(), ccrs.PlateCarree(), ls='-', ec='k', fc='None', lw=0.2, zorder=3)
    ax.set_xticks(np.arange(70, 141, 15), crs=ccrs.PlateCarree())
    ax.set_xticks([], minor=True, crs=ccrs.PlateCarree())
    ax.set_xticklabels(['70°E', '85°E', '100°E', '115°E', '130°E'], fontsize=6)
    ax.set_yticks(np.arange(10, 61, 10), crs=ccrs.PlateCarree())
    ax.set_yticks([], minor=True, crs=ccrs.PlateCarree())
    ax.set_yticklabels(['10°N', '20°N', '30°N', '40°N', '50°N', '60°N'], fontsize=6)

    ax.tick_params(axis='both', width=0.5, length=3)
    ax.tick_params(axis='both', width=0.5, length=1.5, which='minor')
    for spi in ['top', 'bottom', 'left', 'right']:
        ax.spines[spi].set_visible(True)
        ax.spines[spi].set_linewidth(0.5)
    ax.grid(which='major', ls='-.', c='None', alpha=0.6, zorder=5)
    return ax


if __name__ == "__main__":
    cal_nino = CAL_NINO()

    model_prec, model_temp, model_prec_small, model_temp_small = cal_nino.atm()
    lon, lat = model_prec[0]['lon'], model_prec[0]['lat']
    xlon, xlat = model_prec_small[0]['lon'], model_prec_small[0]['lat']

    fig, axes = plt.subplots(1, 3, figsize=(18/2.54, 10/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    fig.tight_layout(w_pad=3.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()
    geo_dict = {
        'levels': np.arange(-1.0, 1.01, 0.1),
        'cmap': cmaps.precip4_diff_19lev,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    for n in range(3):
        ax = axes.flat[n]
        ax = plt_share(ax)
        shp = salem.read_shapefile('./plot/china/china.shp')
        data = model_prec[n].assign_coords(lon=(((model_prec[n].lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax.contourf(lon, lat, masked_data, **geo_dict)
        ax.set_title('Precip. {} forecast'.format(labels[n]), fontsize=10, loc='left', fontweight='bold')

    def small_plot(region, data):  #[0.73, 0.2, 0.18, 0.22]  model_prec_small[0]
        ax1 = fig.add_axes(region, projection = ccrs.PlateCarree())
        ax1.set_extent([104, 125, 0, 25])
        ax1.add_feature(cfeature.LAND, ls='-', ec='k', fc='None', lw=0.2, zorder=2)
        ax1.add_geometries(Reader('./plot/china/cnhimap.shp').geometries(), ccrs.PlateCarree(), ls='-', ec='k', fc='None', lw=0.2, zorder=3)
        for spi in ['top', 'bottom', 'left', 'right']:
            ax1.spines[spi].set_visible(True)
            ax1.spines[spi].set_linewidth(0.2)
        shp = salem.read_shapefile('./plot/china/china.shp')
        data = data.assign_coords(lon=(((data.lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax1.contourf(xlon, xlat, masked_data, levels=np.arange(-1.0, 1.01, 0.1), cmap=cmaps.precip4_diff_19lev, extend="both", transform=ccrs.PlateCarree())

    small_plot([-0.25, 0.165, 0.6, 0.1], model_prec_small[0])
    small_plot([0.088, 0.165, 0.6, 0.1], model_prec_small[1])
    small_plot([0.427, 0.165, 0.6, 0.1], model_prec_small[2])

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
    plt.savefig('./pic/precip_china_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
    plt.close()



    fig, axes = plt.subplots(1, 3, figsize=(18/2.54, 10/2.54), subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    fig.tight_layout(w_pad=3.0, h_pad=4.0)
    labels = pd.date_range(start=cal_nino.current_date.strftime('%Y.%m'), periods=13, freq='MS').strftime('%Y%m').tolist()
    geo_dict = {
        'levels': np.arange(-4.0, 4.01, 0.4),
        'cmap': cmaps.temp_19lev,
        'extend': 'both', 
        'transform': ccrs.PlateCarree(),
    }
    for n in range(3):
        ax = axes.flat[n]
        ax = plt_share(ax)
        shp = salem.read_shapefile('./plot/china/china.shp')
        data = model_temp[n].assign_coords(lon=(((model_temp[n].lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax.contourf(lon, lat, masked_data, **geo_dict)
        ax.set_title('Temp. {} forecast'.format(labels[n]), fontsize=10, loc='left', fontweight='bold')

    def small_plot(region, data):  #[0.73, 0.2, 0.18, 0.22]  model_prec_small[0]
        ax1 = fig.add_axes(region, projection = ccrs.PlateCarree())
        ax1.set_extent([104, 125, 0, 25])
        ax1.add_feature(cfeature.LAND, ls='-', ec='k', fc='None', lw=0.2, zorder=2)
        ax1.add_geometries(Reader('./plot/china/cnhimap.shp').geometries(), ccrs.PlateCarree(), ls='-', ec='k', fc='None', lw=0.2, zorder=3)
        for spi in ['top', 'bottom', 'left', 'right']:
            ax1.spines[spi].set_visible(True)
            ax1.spines[spi].set_linewidth(0.2)
        shp = salem.read_shapefile('./plot/china/china.shp')
        data = data.assign_coords(lon=(((data.lon + 180) % 360) - 180))
        data = data.sortby('lon')
        masked_data = data.salem.roi(shape=shp)
        dplot = ax1.contourf(xlon, xlat, masked_data, levels=np.arange(-4.0, 4.01, 0.4), cmap=cmaps.temp_19lev, extend="both", transform=ccrs.PlateCarree())

    small_plot([-0.25, 0.165, 0.6, 0.1], model_temp_small[0])
    small_plot([0.088, 0.165, 0.6, 0.1], model_temp_small[1])
    small_plot([0.427, 0.165, 0.6, 0.1], model_temp_small[2])

    cbar_color = {
        'orientation': 'horizontal', 
        'shrink': 0.7, 
        'pad': 0.08, 
        'fraction': 0.05, 
        'aspect': 60,
    }
    cbar = plt.colorbar(dplot, ax=axes, **cbar_color)
    cbar.outline.set_linewidth(0.5)
    cbar.set_ticks(np.arange(-4.0, 4.01, 0.8))
    cbar.ax.tick_params(labelsize=6, length=1.5, direction='in', which='major', width=0.5,)
    cbar.ax.tick_params(labelsize=6, length=0.0, direction='in', which='minor', width=0.5,)
    plt.savefig('./pic/temp_china_{}_{}.svg'.format(cal_nino.current_yr, str(cal_nino.current_mon).zfill(2)), bbox_inches='tight')
    plt.close()