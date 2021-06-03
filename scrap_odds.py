#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import requests
from bs4 import BeautifulSoup

def scrap_odds(date, place, race):
    places = {'桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6, '蒲郡': 7,
              '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '琵琶湖': 11, '住之江': 12, '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18, '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24,}
              
    if len(date) == 6:
        date = f'20{date}'

    placeid = int(place) if place.isdigit() else places[place]
    print(date, f"{placeid:02}", race)

    target_url = f'https://www.boatrace.jp/owpc/pc/race/odds3t?rno={race}&jcd={placeid:02}&hd={date}'
    print(target_url)

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

    matrix = []
    for i in range(6):
        matrix.append([])
        for j in range(5):
            matrix[i].append([])
            for k in range(4):
                matrix[i][j].append(0)

    for a1 in range(6):
        for i in range(20):
            idx = i * 6 + a1
            a2 = int(i / 4)
            a3 = i % 4

            if tds[idx].get_text().isdigit():
                odds_value = float(tds[idx].get_text())
                matrix[a1][a2][a3] = odds_value
            else:
                matrix[a1][a2][a3] = 1


    odds_table = {}

    for i in range(6):
        a1 = i
        a2 = 0
        odds_table[f"{a1 + 1}"] = {}
        for j in range(5):
            if a2 == a1:
                a2 += 1

            odds_table[f"{a1 + 1}"][f"{a2 + 1}"] = {}
            a3 = 0
            for k in range(4):
                while a1 == a3 or a2 == a3:
                    a3 += 1

                # print(f"{a1 + 1}-{a2 + 1}-{a3 + 1}: {matrix[i][j][k]:3.1f}")
                odds_table[f"{a1 + 1}"][f"{a2 + 1}"][f"{a3 + 1}"] = matrix[i][j][k]

                a3 += 1
            
            a2 += 1


    jsonfilename = f"odds/o{date[2:]}{placeid:02}{int(race):02}.json"
    with open(jsonfilename, 'w', encoding='utf-8') as jf:
        json.dump(odds_table, jf, ensure_ascii=False, indent=4)
        print(f'output: {jsonfilename}')

        return jsonfilename

if __name__ == '__main__':
    if len(sys.argv) == 4:
        scrap_odds(sys.argv[1], sys.argv[2], sys.argv[3], )
    else:
        print("scrap_odds date place race")
