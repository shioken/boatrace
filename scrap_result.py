#!/usr/bin/env python3
import urllib
import requests
import os

target_url = 'http://www1.mbrace.or.jp/od2/'

years = [2016, 2017, 2018, 2019, 2020, 2021]

for year in years:
    for month in range(1, 13):
        sy = str(year)
        sy2 = sy[2:]
        sm = str(month).zfill(2)

        k_dir = f'{target_url}K/{sy}{sm}/'
        b_dir = f'{target_url}B/{sy}{sm}/'

        print(k_dir, b_dir)

        for day in range(1, 32):
            sd = str(day).zfill(2)

            k_filename = f'k{sy2}{sm}{sd}.lzh'
            b_filename = f'b{sy2}{sm}{sd}.lzh'

            k_lurl = f'{k_dir}{k_filename}'
            b_lurl = f'{b_dir}{b_filename}'
            print(k_lurl, b_lurl)

            k_save_dir = f'k_lzh/{k_filename}'
            b_save_dir = f'b_lzh/{b_filename}'

            if not os.path.exists(k_save_dir):
                try:
                    with urllib.request.urlopen(k_lurl) as res:
                        with open(k_save_dir, mode='wb') as f:
                            f.write(res.read())
                except:
                    print("skip")

            if not os.path.exists(b_save_dir):
                try:
                    with urllib.request.urlopen(b_lurl) as res:
                        with open(b_save_dir, mode='wb') as f:
                            f.write(res.read())
                except:
                    print("skip")
