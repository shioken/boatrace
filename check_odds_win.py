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
    # print(year, month, day, placeid, racenumber)

    prefile = f"predicted/p{year}{month}{day}.json"
    if not os.path.exists(prefile):
        print(f"予測ファイル {prefile} が存在しません")
        return
    
    with open(filename, 'r', encoding='utf-8') as of, open(prefile, 'r', encoding='utf-8') as pf:
        oj = json.load(of)
        pj = json.load(pf)

        for place in pj["places"]:
            if placeid == places[place["name"]]:
                for race in place["races"]:
                    if racenumber == race["number"]:
                        racers = race["racers"]

                        total_score = sum(map(lambda p: p["score"], racers))

                        odds_array = []
                        for racer in racers:
                            real_odds = 1 / (racer["score"] / total_score)
                            odds_array.append(real_odds)

                        vote_array = []
                        for i, odds in enumerate(oj):
                            if odds_array[i] < odds["win"]:
                                # print(f"{i + 1:>2} {odds_array[i]:>5.1f} {odds['win']:>5.1f}")
                                vote_array.append({"order": i + 1, "calc_odds": odds_array[i], "real_odds": odds["win"]})

                        vote_array.sort(key=lambda o: o["calc_odds"])

                        filtered_array = []
                        total_bet = 0
                        min_ret = 1000000
                        for vote in vote_array:
                            total_bet += 100
                            min_ret = min_ret if min_ret < vote["real_odds"] * 100 else vote["real_odds"] * 100
                            if total_bet < min_ret:
                                filtered_array.append(vote)
                            else:
                                break

                        votesfile = f"votes_odds/vw{fn[1:]}"
                        with open(votesfile, 'w', encoding='utf-8') as vf:
                            json.dump(filtered_array, vf, ensure_ascii=False, indent=4)
                            print(f"out: {votesfile}")
                            return votesfile

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
