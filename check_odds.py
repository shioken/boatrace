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

                        for racer in racers:
                            print(racer["course"], racer["score"], racer["score"] / total_score)

                        scores = list(map(lambda p: p["score"] / total_score, racers))

                        score_matrix = {}
                        total_ratio = 0
                        for i in range(6):
                            a1 = i
                            a2 = 0

                            score_matrix[a1] = {}

                            delta_a2 = total_score - scores[a1]

                            for j in range(5):
                                if a1 == a2:
                                    a2 += 1

                                score_matrix[a1][a2] = {}

                                delta_a3 = delta_a2 - scores[a2]
                                
                                a3 = 0
                                for k in range(4):
                                    if a1 == a3:
                                        a3 += 1
                                    if a2 == a3:
                                        a3 += 1
                                
                                    score_odds = 1 / (scores[a1] * scores[a2] / delta_a2 * scores[a3] / delta_a3)
                                    real_odds = oj[f"{a1 + 1}"][f"{a2 + 1}"][f"{a3 + 1}"]

                                    score_matrix[a1][a2][a3] = {"order": f"{a1 + 1}-{a2 + 1}-{a3 + 1}", "calculated_odds": score_odds, "real_odds": real_odds}

                                    total_ratio += 1 / score_odds

                                    a3 += 1

                                a2 += 1

                        high_expectations = []
                        for a1 in score_matrix.keys():
                            sm1 = score_matrix[a1]
                            for a2 in sm1.keys():
                                sm2 = score_matrix[a1][a2]
                                for a3 in sm2.keys():
                                    score_matrix[a1][a2][a3]['calculated_odds'] /= total_ratio

                                    score_odds = score_matrix[a1][a2][a3]['calculated_odds']
                                    real_odds = score_matrix[a1][a2][a3]['real_odds']
                                    starmark = ""
                                    if score_odds < real_odds:
                                        starmark = "*"
                                        ticket = {"order": f"{a1 + 1}-{a2 + 1}-{a3 + 1}",
                                                  "calculated_odds": score_odds, "real_odds": real_odds}
                                        high_expectations.append(ticket)
                                    


                        print("")
                        high_expectations.sort(key=lambda o: o["calculated_odds"])
                        for exp in high_expectations:
                            print(f"{exp['order']} {exp['calculated_odds']:>8.3f} {exp['real_odds']:>8.3f}")


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
