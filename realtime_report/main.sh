#!/bin/bash

current_yr=2023
current_mon=04

# 1. post processing OBS dataset
bash ./OBS/done.sh

# 2. post processing model dataset
bash ./read_data/done.sh $current_yr $current_mon

# 3. plot
python3.8 ./plot/f1_Nino_index.py $current_yr $current_mon
python3.8 ./plot/f2_ssta_evolution.py $current_yr $current_mon
python3.8 ./plot/f3_CP_IOD_index.py $current_yr $current_mon
python3.8 ./plot/f4_ssta_global.py $current_yr $current_mon
python3.8 ./plot/f5_hgt_uv_global.py $current_yr $current_mon
python3.8 ./plot/f6_pr_temp_land.py $current_yr $current_mon
python3.8 ./plot/f7_pr_temp_china.py $current_yr $current_mon

# 4. make PPT
python3.8 ./pic/makePPT.py $current_yr $current_mon

rm -rf ./tmp/*.nc 
rm -rf ./pic/*.svg