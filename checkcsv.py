#!/usr/bin/env python3
import pandas as pd
import glob
import re

files = sorted(glob.glob('csv/m*.csv'), reverse=True)

for file in files:
    df = pd.read_csv(file)
    print(file)
    df['number'].astype('float32')
    df['weight'].astype('float32')
