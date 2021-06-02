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

def inquire(target):
    votefile = f'votes/v{target}.json'
    resultfile = f'json/m{target}.json'
    
    if not os.path.exists(votefile):
        print(f'{votefile} is not exists')
        return
    
    if not os.path.exists(resultfile):
        print(f'{resultfile} is not exists')
        return

    with open(votefile, 'r', encoding='utf-8') as vf, open(resultfile, 'r', encoding='utf-8') as rf:
        vjson = json.load(vf)
        rjson = json.load(rf)

        tierce_count = 0
        tierce_inquire = 0
        trio_count = 0
        trio_inquire = 0
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
                    # print(f"{race['number']}R 3連単: {order[0]}-{order[1]}-{order[2]} 配当{result['tierce']:6,} / 3連複: {sorted_order[0]}-{sorted_order[1]}-{sorted_order[2]} 配当 {result['trio']:6,}")
                    vline = f"{race['number']:2}R 3連単: {order[0]}-{order[1]}-{order[2]} 配当{result['tierce']:6,} / 3連複: {sorted_order[0]}-{sorted_order[1]}-{sorted_order[2]} 配当 {result['trio']:6,}"
                    vline += " "
                    for vote in race["votes"]:
                        bet = (int(vote[0:1]), int(vote[2:3]), int(vote[4:5]))
                        trio_bet = sorted(bet)

                        total_bet += 100

                        vline += vote
                        if bet == order:
                            vline += '*'
                            tierce_count += 1
                            tierce_inquire += result['tierce']
                            trio_inquire += result['trio']
                            trio_count += 1
                        elif sorted_order == trio_bet:
                            vline += '#'
                            trio_count += 1
                            trio_inquire += result['trio']
                        else:
                            vline += " "
                        
                        vline += " "
                    print(vline)

                    total_all_bet += result['tierce']
                else:
                    print(f"{race['number']}R レース不成立")


        print("")        
        print(f"レース数:{total_race}, 総投資額:{total_bet:8,} 3連単({tierce_count:2}):{tierce_inquire:8,}({tierce_inquire - total_bet:8,}) 3連複({trio_count:2}):{trio_inquire:8,}(({trio_inquire - total_bet:8,})")
        print(
            f"回収率 3連単:{tierce_inquire / total_bet * 100:6.2f}% 3連複:{trio_inquire / total_bet * 100:6.2f}%")

        print(f"3連単全掛: {total_all_bet:8,} 回収率: {total_all_bet / (total_race * 100 * 120) * 100:6.2f}%")
if __name__ == '__main__':
    if len(sys.argv) == 2:
        inquire(sys.argv[1])
    else:
        print("Please specify a file.")