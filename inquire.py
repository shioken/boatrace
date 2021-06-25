#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import utils

def search_result(result, place, number):
    for race in result:
        if race["place"] == place and race["racenumber"] == number:
            if 'result' in race:
                return race["result"]
            else:
                return None

    return None

def inquire(target, type):

    prefix = 'n' if type == 'nn' else 'l'

    votefile = f'votes/{prefix}{target}.json'
    resultfile = f'json/m{target}.json'
    
    if not os.path.exists(votefile):
        print(f'{votefile} is not exists')
        return None
    
    if not os.path.exists(resultfile):
        print(f'{resultfile} is not exists')
        return None

    year = 2000 + int(target[:2])
    month = int(target[2:4])
    day = int(target[4:])

    with open(votefile, 'r', encoding='utf-8') as vf, open(resultfile, 'r', encoding='utf-8') as rf:
        vjson = json.load(vf)
        rjson = json.load(rf)

        tierce_one_count = 0
        tierce_one_inquire = 0
        tierce_count = 0
        tierce_inquire = 0
        trio_count = 0
        trio_inquire = 0
        trio_one_count = 0
        trio_one_inquire = 0
        total_bet = 0
        total_race = 0
        total_bet_race = 0
        total_bet_win_race = 0
        win_count = 0
        win_inquire = 0

        for place in vjson:
            print("------------------------------------------------------------")
            print(place["name"])

            tierce_place_bet = 0
            tierce_place_inquire = 0
            win_place_bet = 0
            win_place_inquire = 0
            
            for race in place["races"]:
                result = search_result(rjson, place["name"], race["number"])
                if result is None:
                    print(f"{race['number']:2}R 結果なし")
                    continue

                order = (result["1st"], result["2nd"], result["3rd"],)
                sorted_order = sorted(order)
                if sorted_order[0] > 0:
                    total_race += 1
                    if not 'win' in result:
                        print(target, result)
                    vline = f"{race['number']:2}R 3連単: {order[0]}-{order[1]}-{order[2]} 配当{result['tierce']:8,} / 3連複: {sorted_order[0]}-{sorted_order[1]}-{sorted_order[2]} 配当 {result['trio']:8,} / 単勝: {order[0]} 配当 {result['win']:6,}"
                    vline += " "
                    isRaceWin = [False, False]
                    for no, vote in enumerate(race["votes"]):
                        bet = (int(vote[0:1]), int(vote[2:3]), int(vote[4:5]))
                        trio_bet = sorted(bet)

                        total_bet += 100
                        tierce_place_bet += 100

                        if no == 0:
                            total_bet_race += 1             # Betしたレース


                        vline += vote
                        if bet == order:
                            vline += '*'

                            tierce_count += 1
                            tierce_inquire += result['tierce']
                            tierce_place_inquire += result['tierce']

                            trio_count += 1
                            trio_inquire += result['trio']

                            if no == 0:
                                tierce_one_count += 1
                                tierce_one_inquire += result['tierce']
                                trio_one_count += 1
                                trio_one_inquire += result['trio']

                            isRaceWin[0] = True
                            isRaceWin[1] = True
                        elif sorted_order == trio_bet:
                            vline += '#'

                            trio_count += 1
                            trio_inquire += result['trio']

                            if no == 1:
                                trio_one_count += 1
                                trio_one_inquire += result['trio']

                            isRaceWin[1] = True
                        else:
                            vline += " "
                        
                        vline += " "

                    if 'votewin' in race:
                        for vote_win in race['votewin']:
                            total_bet_win_race += 1
                            win_place_bet += 100
                            vline += f"{vote_win}"
                            if vote_win == result['1st']:
                                vline += "*"
                                win_count += 1
                                win_inquire += result['win']
                                win_place_inquire += result['win']
                            else:
                                vline += " "

                    print(vline)
                else:
                    print(f"{race['number']}R レース不成立")
            print("")
            print(f"{place['name']}")
            print(f"3連単: 購入{tierce_place_bet:8,} 払戻 {tierce_place_inquire:>8,} ({tierce_place_inquire - tierce_place_bet:> 8,})")
            print(f"単勝 : 購入{win_place_bet:8,} 払戻 {win_place_inquire:>8,} ({win_place_inquire - win_place_bet:> 8,})")
            print("")


        print("")
        print(f"{year}/{month:02}/{day:02}")
        if total_bet > 0 and total_race > 0:
            print(f"レース数:{total_race} 参加レース数: {total_bet_race} 単勝/3連単x1/3連複x1: {total_bet_win_race} 3連単x4: {total_bet:>8,}")
            print(f"3連単x4({tierce_count:3}):{tierce_inquire:8,}({tierce_inquire - total_bet:>8,})")
            print(f"3連複x4({trio_count:3}):{trio_inquire:8,}({trio_inquire - total_bet:>8,})")
            print(f"3連単x1({tierce_one_count:3}):{tierce_one_inquire:8,}({tierce_one_inquire - total_bet_race * 100:>8,})")
            print(f"3連複x1({trio_one_count:3}):{trio_one_inquire:8,}({trio_one_inquire - total_bet_race * 100:>8,})")
            print(f"単勝   ({win_count:3}):{win_inquire:8,}({win_inquire - total_bet_win_race * 100:>8,})")
            print(f"\n当選率")
            print(f"3連単x4:{tierce_count / total_bet_race * 100:8.2f}%")
            print(f"3連複x4:{trio_count / total_bet_race * 100:8.2f}%")
            print(f"3連単x1:{tierce_one_count / total_bet_race * 100:8.2f}%")
            print(f"3連複x1:{trio_one_count / total_bet_race * 100:8.2f}%")
            print(f"単勝   :{win_count / total_bet_win_race * 100:8.2f}%")
            print(f"\n回収率")
            print(f"3連単x4:{tierce_inquire / total_bet * 100:8.2f}%")
            print(f"3連複x4:{trio_inquire / total_bet * 100:8.2f}%")
            print(f"3連単x1:{tierce_one_inquire / (total_bet_race * 100) * 100 :8.2f}%")
            print(f"3連複x1:{trio_one_inquire / (total_bet_race * 100) * 100 :8.2f}%")
            print(f"単勝   :{win_inquire / total_bet_win_race:>8.2f}%")

        return (total_race, total_bet_race, total_bet, tierce_count, tierce_inquire, trio_count, trio_inquire, tierce_one_count, tierce_one_inquire, win_count, win_inquire)


if __name__ == '__main__':
    date = ""
    if len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today' or date == 't':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()

    if len(sys.argv) == 3:
        inquire(date, sys.argv[2])
    elif len(sys.argv) == 2:
        inquire(date, 'nn')
        inquire(date, 'lm')
    else:
        print("Please specify a file.")
