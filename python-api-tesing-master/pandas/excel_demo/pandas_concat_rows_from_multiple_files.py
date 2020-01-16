#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:    xurongzhong#126.com wechat:pythontesting qq:37391319
# CreateDate: 2018-1-19 pandas_concat_rows_from_multiple_files.py
import pandas as pd
import glob
import os

input_path = os.path.dirname(__file__)           # current file path
output_file = r"output_files\12output.csv"

all_files = glob.glob(os.path.join(input_path, 'sales_*'))    #
all_data_frames = []
for file in all_files:
    print(file.replace("\\", "/"))
    data_frame = pd.read_csv(file.replace("\\", "/"), index_col=None)
    all_data_frames.append(data_frame)
data_frame_concat = pd.concat(all_data_frames, axis=0, ignore_index=True)
data_frame_concat.to_csv(output_file, index=False)