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

    placeid = places[place]
    print(date, f"{placeid:02}", race)

    target_url = f'https://www.boatrace.jp/owpc/pc/race/odds3t?rno={race}&jcd={placeid:02}&hd={date}'

    r = requests.get(target_url)
    soup = BeautifulSoup(r.text, "html.parser")

    # table = soup.select('tbody.is-p3-0')
    tds = soup.select('td.oddsPoint')

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

            odds_value = float(tds[idx].get_text())
            matrix[a1][a2][a3] = odds_value

    for i in range(6):
        a1 = i
        a2 = 0
        for j in range(5):
            if a2 == a1:
                a2 += 1

            a3 = 0
            for k in range(4):
                if a3 == a1:
                    a3 += 1
                if a3 == a2:
                    a3 += 1

                print(f"{a1 + 1}-{a2 + 1}-{a3 + 1}: {matrix[i][j][k]:3.1f}")

                a3 += 1
            
            a2 += 1




if __name__ == '__main__':
    if len(sys.argv) == 4:
        scrap_odds(sys.argv[1], sys.argv[2], sys.argv[3], )
    else:
        print("scrap_odds date place race")
