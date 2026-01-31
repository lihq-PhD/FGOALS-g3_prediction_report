#!/bin/bash

current_yr=$1
current_mon=$2

cd ./tmp

members1=( F A )
members2=( 01_00_C0100 01_00_C0200 02_00_C0100 02_00_C0200 )

# 1. members
for m1 in ${members1[@]}; do
    for m2 in ${members2[@]}; do
        for ld in 1 2 3 4 5 6 7 8 9 10 11 12 13; do
            thetao_rootPath=/mnt/disk3/FG3_hindcast_v1.0/postData/${m1}_${m2}/thetao_${m1}${m2}_lead${ld}_1990-2020clim_anom.nc
            cdo seldate,$1-$2-01,2050-01-01 -sellevel,5 ${thetao_rootPath} thetao_tmp1.nc 
            cdo seltimestep,${ld} thetao_tmp1.nc thetao_tmp2_${ld}.nc

            atm3D_rootPath=/mnt/disk3/FG3_hindcast_v1.0/postData/${m1}_${m2}/atm3D_${m1}${m2}_lead${ld}_1990-2020clim_anom.nc
            cdo seldate,$1-$2-01,2050-01-01 -selname,PRECT,ts ${atm3D_rootPath} atm3D_tmp1.nc 
            cdo seltimestep,${ld} atm3D_tmp1.nc atm3D_tmp2_${ld}.nc

            atm4D_rootPath=/mnt/disk3/FG3_hindcast_v1.0/postData/${m1}_${m2}/atm4D_${m1}${m2}_lead${ld}_1990-2020clim_anom.nc
            cdo seldate,$1-$2-01,2050-01-01 -sellevel,200,500,850 -selname,U,V,hgt ${atm4D_rootPath} atm4D_tmp1.nc 
            cdo seltimestep,${ld} atm4D_tmp1.nc atm4D_tmp2_${ld}.nc
        done

        cdo mergetime thetao_tmp2_*.nc thetao_${m1}${m2}.nc
        cdo mergetime atm3D_tmp2_*.nc atm3D_${m1}${m2}.nc
        cdo mergetime atm4D_tmp2_*.nc atm4D_${m1}${m2}.nc
        rm -rf thetao_tmp1.nc thetao_tmp2_*.nc atm3D_tmp1.nc atm3D_tmp2_*.nc atm4D_tmp1.nc atm4D_tmp2_*.nc
    done
done

# 2. MME  F01_00_C0100
cdo ensmean thetao_????????????.nc thetao_MME.nc
cdo ensmean atm3D_????????????.nc atm3D_MME.nc
cdo ensmean atm4D_????????????.nc atm4D_MME.nc
rm -rf atm3D_????????????.nc atm4D_????????????.nc