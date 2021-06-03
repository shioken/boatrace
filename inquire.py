#!/usr/bin/env python3
import glob
import re
import os
import json
import sys

def search_result(result, place, number):
    for race in result:
        if race["place"] == place and race["racenumber"] == number:
            return race["result"]

    return None

def inquire(target, minthreshold = 0.0, maxthreshold = 1.0):

    votefile = f'votes/v{target}.json'
    resultfile = f'json/m{target}.json'
    
    if not os.path.exists(votefile):
        print(f'{votefile} is not exists')
        return
    
    if not os.path.exists(resultfile):
        print(f'{resultfile} is not exists')
        return

    year = 2000 + int(target[:2])
    month = int(target[2:4])
    day = int(target[4:])

    with open(votefile, 'r', encoding='utf-8') as vf, open(resultfile, 'r', encoding='utf-8') as rf:
        vjson = json.load(vf)
        rjson = json.load(rf)

        tierce_count = 0
        tierce_inquire = 0
        tierce_std = 0.0
        trio_count = 0
        trio_inquire = 0
        trio_std = 0.0
        out_tierce_std = 0.0
        out_tierce_count = 0
        out_trio_std = 0.0
        out_trio_count = 0
        total_bet = 0
        total_race = 0

        total_all_bet = 0

        for place in vjson:
            print(place["name"])
            for race in place["races"]:
                result = search_result(rjson, place["name"], race["number"])
                order = (result["1st"], result["2nd"], result["3rd"],)
                sorted_order = sorted(order)
                if sorted_order[0] > 0:
                    total_race += 1
                    vline = f"{race['number']:2}R 3連単: {order[0]}-{order[1]}-{order[2]} 配当{result['tierce']:8,} / 3連複: {sorted_order[0]}-{sorted_order[1]}-{sorted_order[2]} 配当 {result['trio']:8,}"
                    vline += " "
                    if race["std"] >= minthreshold and race["std"] <= maxthreshold:
                        isRaceWin = [False, False]
                        for vote in race["votes"]:
                            bet = (int(vote[0:1]), int(vote[2:3]), int(vote[4:5]))
                            trio_bet = sorted(bet)

                            total_bet += 100

                            vline += vote
                            if bet == order:
                                vline += '*'

                                tierce_count += 1
                                tierce_inquire += result['tierce']
                                tierce_std += race["std"]

                                trio_count += 1
                                trio_inquire += result['trio']
                                trio_std += race["std"]

                                isRaceWin[0] = True
                                isRaceWin[1] = True
                            elif sorted_order == trio_bet:
                                vline += '#'

                                trio_count += 1
                                trio_inquire += result['trio']
                                trio_std += race["std"]

                                isRaceWin[1] = True
                            else:
                                vline += " "
                            
                            vline += " "

                        if isRaceWin[0] is False:
                            out_tierce_std += race["std"]
                            out_tierce_count += 1
                        if isRaceWin[1] is False:
                            out_trio_std += race["std"]
                            out_trio_count += 1

                        print(vline)

                        total_all_bet += result['tierce']
                else:
                    print(f"{race['number']}R レース不成立")


        print("")
        print(f"{year}/{month:02}/{day:02}")
        if total_bet > 0 and total_race > 0:
            print(f"レース数:{total_race}, 総投資額:{total_bet:8,} 3連単({tierce_count:2}):{tierce_inquire:8,}({tierce_inquire - total_bet:8,}) 3連複({trio_count:2}):{trio_inquire:8,}({trio_inquire - total_bet:8,})")
            print(f"当選率 3連単:{tierce_count / total_race * 100:8.2f}% 3連複:{trio_count / total_race * 100:6.2f}%")
            print(f"回収率 3連単:{tierce_inquire / total_bet * 100:8.2f}% 3連複:{trio_inquire / total_bet * 100:6.2f}%")

        print("")
        if tierce_count > 0 and trio_count > 0:
            print(f"3連単 当選標準偏差:{tierce_std / tierce_count:1.5f}/非当選:{out_tierce_std / out_tierce_count:1.5f} 3連複 当選標準偏差:{trio_std / trio_count:1.5f}/非当選:{out_trio_std / out_trio_count:1.5f}")

if __name__ == '__main__':
    if len(sys.argv) == 4:
        inquire(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
    if len(sys.argv) == 3:
        inquire(sys.argv[1], float(sys.argv[2]))
    elif len(sys.argv) == 2:
        inquire(sys.argv[1])
    else:
        print("Please specify a file.")
