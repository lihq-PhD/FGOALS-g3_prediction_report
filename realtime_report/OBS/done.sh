#!/bin/bash

cd /home/sunming/data5/Lihaoq/PhD/FGOALS-g3_prediction_report/realtime_report

cd ./tmp

# 1. update HadISST dataset
wget -c https://www.metoffice.gov.uk/hadobs/hadisst/data/HadISST_sst.nc.gz
gzip -d HadISST_sst.nc.gz

# 2. post processing
cdo selname,sst HadISST_sst.nc tmp1.nc 
cdo remapbil,r360x181 tmp1.nc tmp2.nc 
cdo setreftime,1870-01-01,00:00:00,1days -settaxis,1870-01-01,00:00:00,1months -setcalendar,standard tmp2.nc tmp3.nc
cdo ymonmean -selyear,1991/2020 tmp3.nc tmp4.nc
cdo ymonsub tmp3.nc tmp4.nc HadISST_ssta_1x1.nc
rm -rf tmp?.nc
rm -rf HadISST_sst.nc