#!/usr/bin/env python3
import urllib
import requests

target_url = 'http://www1.mbrace.or.jp/od2/K/'

years = [2016, 2017, 2018, 2019, 2020, 2021]

for year in years:
    for month in range(1, 13):
        sy = str(year)
        sy2 = sy[2:]
        sm = str(month).zfill(2)

        dir = f'{target_url}{sy}{sm}/'

        for day in range(1, 32):
            sd = str(day).zfill(2)

            filename = f'k{sy2}{sm}{sd}.lzh'

            lurl = f'{dir}{filename}'
            print(lurl)

            save_dir = f'r_lzh/{filename}'

            with urllib.request.urlopen(lurl) as res:
                with open(save_dir, mode='wb') as f:
                    f.write(res.read())

