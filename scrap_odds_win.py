#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import requests
from bs4 import BeautifulSoup


def scrap_odds(date, place, race, writeFile=True):
    places = {'桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6, '蒲郡': 7,
              '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '琵琶湖': 11, '住之江': 12, '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18, '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24, }

    if len(date) == 6:
        date = f'20{date}'

    placeid = int(place) if place.isdigit() else places[place]
    # print(date, f"{placeid:02}", race)

    target_url = f'https://www.boatrace.jp/owpc/pc/race/oddstf?rno={race}&jcd={placeid:02}&hd={date}'
    # print(target_url)

    try:
        r = requests.get(target_url)
        r.raise_for_status()
    except:
        print("An error occurred while retrieving the web page.")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    # table = soup.select('tbody.is-p3-0')
    tds = soup.select('td.oddsPoint')

    if len(tds) == 0:
        return

    odds = []
    if len(tds) >= 6:
        for i, td in enumerate(tds):
            c = i % 6
            if i < 6:
                tdtext = td.get_text()
                rate = {"win": 1 if '欠場' in tdtext else float(tdtext)}
                odds.append(rate)
            else:
                odds[c]["double_win"] = td.get_text()

    if writeFile:
        jsonfilename = f"odds/w{date[2:]}{placeid:02}{int(race):02}.json"
        with open(jsonfilename, 'w', encoding='utf-8') as jf:
            json.dump(odds, jf, ensure_ascii=False, indent=4)
            print(f'output: {jsonfilename}')

        return jsonfilename
    else:
        for i, racer in enumerate(odds):
            print(f"{i + 1} {racer['win']:>4.1f} {racer['double_win']}")
    
    return odds

if __name__ == '__main__':
    if len(sys.argv) == 4:
        scrap_odds(sys.argv[1], sys.argv[2], sys.argv[3], )
    else:
        print("scrap_odds date place race")
