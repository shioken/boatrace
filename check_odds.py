#!/usr/bin/env python3
import glob
import re
import os
import json
import sys

places = {'桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6, '蒲郡': 7,
          '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '琵琶湖': 11, '住之江': 12, '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18, '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24, }

def check_odds(filename):
    if not os.path.exists(filename):
        print(f"オッズファイル {filename} が存在しません")
        return

    fn = os.path.basename(filename)
    year = fn[1:3]
    month = fn[3:5]
    day = fn[5:7]
    placeid = int(fn[7:9])
    racenumber = int(fn[9:11])
    print(year, month, day, placeid, racenumber)

    prefile = f"predicted/p{year}{month}{day}.json"
    if not os.path.exists(prefile):
        print(f"予測ファイル {prefile} が存在しません")
        return
    
    with open(filename, 'r', encoding='utf-8') as of, open(prefile, 'r', encoding='utf-8') as pf:
        oj = json.load(of)
        pj = json.load(pf)

        for place in pj["places"]:
            if placeid == places[place["name"]]:
                print("found: ", place["name"])
                for race in place["races"]:
                    if racenumber == race["number"]:
                        print(race["name"])
                        racers = race["racers"]

                        total_score = sum(map(lambda p: p["score"], racers))
                        print(total_score)
                        for racer in racers:
                            print(racer["course"], racer["score"], racer["score"] / total_score)

                        for i in range(6):
                            a1 = i
                            a2 = 0
                            for j in range(5):
                                if a1 == a2:
                                    a2 += 1
                                
                                a3 = 0
                                for k in range(4):
                                    if a1 == a3:
                                        a3 += 1
                                    if a2 == a3:
                                        a3 += 1
                                
                                    ratio = 1 / (racers[a1]["score"] / total_score * racers[a2]["score"] / total_score * racers[a3]["score"] / total_score)
                                    real_odds = oj[f"{a1 + 1}"][f"{a2 + 1}"][f"{a3 + 1}"]

                                    starmark = ""
                                    if ratio < real_odds:
                                        starmark = "*"
                                    print(f"{a1 + 1}-{a2 + 1}-{a3 + 1} {ratio:>10.7f} : {real_odds} {starmark}")

                                    a3 += 1


                                a2 += 1


def parseRace(date, place, race):
    if len(date) == 4:
        date = date[2:]

    if not place in places:
        print("場所が不正です")
        return

    placeid = places[place]

def parseFile(filename):
    check_odds(filename)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        parseFile(sys.argv[1])
    elif len(sys.argv) == 4:
        parseRace(sys.argv[1], sys.argv[2], sys.argv[3])
