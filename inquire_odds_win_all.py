#!/usr/bin/env python3
import glob
import os
import sys
import json

places = {'桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6, '蒲郡': 7,
          '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '琵琶湖': 11, '住之江': 12, '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18, '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24, }

def check_all_inquire(date):
    files = glob.glob(f'votes_odds/vw{date}*.json')

    all_bet = 0
    all_return = 0
    all_hit = 0
    all_race_count = 0
    for file in files:
        basename = os.path.basename(file)
        date = basename[1:7]
        placeid = int(basename[7:9])
        racenumber = int(basename[9:11])

        resultfile = f"json/m{date}.json"

        with open(file, 'r', encoding='utf-8') as vf, open(resultfile, 'r', encoding='utf-8') as rf:
            votes = json.load(vf)
            races = json.load(rf)

            # レースを探す
            all_place_bet = 0
            all_place_return = 0
            for race in races:
                if placeid == places[race["place"]] and racenumber == race["racenumber"]:
                    result_set = race["result"]
                    if result_set['1st'] > -1:
                        line = f"{race['place']:　<3} {racenumber:>2}R "
                        tierce_set = f"{result_set['1st']}-{result_set['2nd']}-{result_set['3rd']}"
                        tierce_val = result_set["tierce"]
                        # print(tierce_set, tierce_val)
                        line += f"{tierce_set} {tierce_val:>8,} "
                        # votes_count = len(votes)
                        votes_count = 0
                        line += f"購入点数:{votes_count:>4} {100 * votes_count:>8,} "
                        for vote in votes:
                            if vote["calculated_odds"] < 9999 and vote["calculated_odds"] > 0:  # 値を変動すると倍率を絞れます
                                votes_count += 1
                                if vote["order"] == tierce_set:
                                    line += f"{vote['order']} {tierce_val:>8,}"
                                    all_place_return += tierce_val
                                    all_hit += 1

                        all_race_count += 1
                        all_place_bet += 100 * votes_count
                        print(line)

            all_bet += all_place_bet
            all_return += all_place_return

    if all_bet > 0:
        print(
            f"総投資額: {all_bet:8,} 回収額: {all_return:8,} 収支: {all_return - all_bet:8,} 回収率: {all_return / all_bet * 100:>10.2f}%")
        print(f"総レース数: {all_race_count:>3} 当選レース数: {all_hit:>3} 当選率: {all_hit / all_race_count * 100:>5.2f}")
                    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        check_all_inquire(sys.argv[1])
    else:
        print("check_all_odds date")
