#!/usr/bin/env python3
import os
import sys
import utils
import json
from datetime import datetime as dt
import show_deviation
import scrap_odds_win
import numpy as np
import utils

def show_timelimit(date, limit=10, type="lm"):
    racefile = f'json/m{date}.json'
    if not os.path.exists(racefile):
        print(f"{racefile} is not exists.")
        return
    
    with open(racefile, 'r', encoding='utf-8') as rf:
        rjson = json.load(rf)

        now = dt.now()
        fnow = dt.now().strftime('%H:%M')

        sorted_race = sorted(rjson, key=lambda x: x['timelimit'])
        filterd_race = filter(lambda x:x['timelimit'] > fnow, sorted_race)
        for i, race in enumerate(filterd_race):
            rdt = dt(year=now.year, month=now.month, day=now.day, hour=int(race['timelimit'][:2]), minute=int(race['timelimit'][3:]))
            diff = rdt - now
            place = race['place']
            placeid = utils.placeid(place)
            racenumber = race['racenumber']
            formatted_place = (race['place'] + "　　　")[:3]
            last_time_min = diff.total_seconds() // 60
            last_time_sec = diff.total_seconds() - last_time_min * 60
            print("")
            print(f"{formatted_place} {race['racenumber']:>2}R {race['timelimit']} あと{last_time_min:>2.0f}分{last_time_sec:>2.0f}秒")
            print("")
            print(f"http://livebb.jlc.ne.jp/bb_top/new_bb/index.php?tpl={placeid}")
            print(f"https://www.boatrace.jp/owpc/pc/race/odds3t?rno={racenumber}&jcd={placeid:02}&hd=20{date}")
            if type == 'nn':
                print("\nnn\n")
                nn = show_deviation.show_deviation(date, 'nn', race['place'], race['racenumber'])

            if type == 'lm':
                print("\nlm\n")
                lm = show_deviation.show_deviation(date, 'lm', race['place'], race['racenumber'])
            # print("\nodds")
            # odds = scrap_odds_win.scrap_odds(date, race['place'], race['racenumber'], False)

            # if not nn is None:
            #     print("\n推定単勝オッズ")
            #     sum = np.sum(nn)
            #     if not odds is None:
            #         for c, (v, o) in enumerate(zip(nn, odds)):
            #             c_odds = sum / v
            #             d = float(o['win'])
            #             mark = "*" if c_odds < d else ' '
            #             print(f"{c + 1} {c_odds:>6.2f} {1 / c_odds * 100: >5.2f}% {mark}")

            if i + 1 == limit:
                break



if __name__ == '__main__':
    limit = 5
    date = utils.getStringToday()
    type = "lm"

    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    
    if len(sys.argv) == 3:
        type = sys.argv[2]
        # date = sys.argv[2]
        # if date == 'today':
        #     date = utils.getStringToday()
        # elif date == 'yesterday':
        #     date = utils.getStringYesterday()

    
    show_timelimit(date, limit, type)
