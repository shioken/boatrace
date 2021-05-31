#!/usr/bin/env python3
import urllib
import requests
import os
from datetime import datetime, timedelta
import sys
import lhafile
import subprocess

target_url = 'http://www1.mbrace.or.jp/od2/'

def getFile(url, filename):
    if not os.path.exists(filename):
        print("get:", url, "->", filename)
        try:
            with urllib.request.urlopen(url) as res:
                with open(filename, mode='wb') as f:
                    f.write(res.read())

                lf = lhafile.Lhafile(filename)
                info = lf.infolist()
                name = info[0].filename
                print(name)

                output_dir = "result" if name[0].upper() == "K" else "racelist"
                txtfilepath = f"{output_dir}/{name.lower()}"
                print(txtfilepath)
                # print(lf.read(name))
                with open(txtfilepath, "wb") as wf:
                    wf.write(lf.read(name))

                cmd = f"nkf -w --overwrite {output_dir}/{name}"
                subprocess.call(cmd, shell=True)

        except KeyboardInterrupt:
            print("Stop for Ctrl+C")
        except:
            print("except")


def scrap_today():
    today = datetime.today()
    stoday = today.strftime("%y%m%d")
    stmonth = today.strftime("%Y%m")
    dir = f'{target_url}B/{stmonth}/'
    filename = f'b{stoday}.lzh'
    lurl = f'{dir}{filename}'
    save_dir = f'b_lzh/{filename}'
    getFile(lurl, save_dir)

def scrap_tommorow():
    tomorrow = datetime.today() + timedelta(days=1)
    stoday = tomorrow.strftime("%y%m%d")
    stmonth = tomorrow.strftime("%Y%m")
    dir = f'{target_url}B/{stmonth}/'
    filename = f'b{stoday}.lzh'
    lurl = f'{dir}{filename}'
    save_dir = f'b_lzh/{filename}'
    getFile(lurl, save_dir)

def scrap(date):
    year = date[:4]
    month = date[4:6]
    day = date[6:8]
    yy = year[2:]
    stoday = f"{yy}{month}{day}"
    stmonth = f"{year}{month}"
    dir = f'{target_url}B/{stmonth}/'
    filename = f'b{stoday}.lzh'
    lurl = f'{dir}{filename}'
    save_dir = f'b_lzh/{filename}'
    getFile(lurl, save_dir)

def scrap_all():
    years = [2016, 2017, 2018, 2019, 2020, 2021]
    days = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    today = datetime.today()
    stoday = today.strftime("%y%m%d")

    for year in years:
        for month in range(1, 13):
            sy = str(year)
            sy2 = sy[2:]
            sm = str(month).zfill(2)

            k_dir = f'{target_url}K/{sy}{sm}/'
            b_dir = f'{target_url}B/{sy}{sm}/'

            for day in range(1, days[month] + 1):
                if month == 2 and day == 29:
                    print(year, month, day)
                    if year % 4 != 0:
                        print("not うるう年")
                        break
                    elif year % 100 == 0:
                        if year % 400 != 0:
                            print("not うるう年")
                            break

                sd = str(day).zfill(2)

                sc = f'{sy2}{sm}{sd}'

                if int(stoday) >= int(sc):
                    k_filename = f'k{sy2}{sm}{sd}.lzh'
                    b_filename = f'b{sy2}{sm}{sd}.lzh'

                    k_lurl = f'{k_dir}{k_filename}'
                    b_lurl = f'{b_dir}{b_filename}'

                    k_save_dir = f'k_lzh/{k_filename}'
                    b_save_dir = f'b_lzh/{b_filename}'

                    getFile(k_lurl, k_save_dir)
                    getFile(b_lurl, b_save_dir)
                else:
                    break


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'today':
            scrap_today()
        elif sys.argv[1] == 'tommorow':
            scrap_tommorow()
        else:
            scrap(sys.argv[1])

    else:
        scrap_all()
