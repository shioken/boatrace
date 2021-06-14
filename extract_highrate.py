#!/usr/bin/env python3
import sys
import os
import json
import numpy as np

predict = None
result = None

def findPredict(place, racenumber):
    for p in predict['places']:
        if p['name'] == place:
            for race in p['races']:
                if racenumber == race['number']:
                    return race

def extract_highrate(date, type, rate=12000):
    global predict, result

    prefix = 'n' if type == 'nn' else 'l'

    predictfile = f'predicted/{prefix}{date}.json'
    resultfile = f'json/m{date}.json'

    if not os.path.exists(predictfile):
        print(f"{predictfile} is not exists")
        return
    
    if not os.path.exists(resultfile):
        print(f"{resultfile} is not exists")
        return
    
    with open(predictfile, 'r', encoding='utf-8') as pf, open(resultfile, 'r', encoding='utf-8') as rf:
        predict = json.load(pf)
        result = json.load(rf)
        
        tierces = []
        tierces_std = []
        trios = []
        trios_std = []
        wins = []
        wins_std = []

        for race in result:
            result = race['result']
            formplace = (result['place'] + "　　")[:3]
            o = [result['1st'], result['2nd'], result['3rd']]
            so = sorted(o)

            std = 0
            predict_race = findPredict(
                result['place'], result['racenumber'])
            if predict_race:
                scores = np.array(
                    list(map(lambda x: x['score'], predict_race['racers'])))
                std = scores.std()
            if result['tierce'] > rate:
                print(f"{formplace} {result['racenumber']:>2}R ３連単 {result['tierce']:>8,} {o[0]}-{o[1]}-{o[2]} {std:>8.6f}")
                tierces.append(result['tierce'])
                tierces_std.append(std)
            
            if result['trio'] > rate / 6:
                print(f"{formplace} {result['racenumber']:>2}R ３連複 {result['trio']:>8,} {so[0]}-{so[1]}-{so[2]} {std:>8.6f}")
                trios.append(result['trio'])
                trios_std.append(std)

            if result['win'] > rate / 20:
                print(f"{formplace} {result['racenumber']:>2}R 単勝   {result['win']:>8,} {o[0]}     {std:>8.6f}")
                wins.append(result['win'])
                wins_std.append(std)

        np_tierces = np.array(tierces)
        np_std_tierces = np.array(tierces_std)
        np_trios = np.array(trios)
        np_trios_std = np.array(trios_std)
        np_wins = np.array(wins)
        np_wins_std = np.array(wins_std)

        print(f"Avg 3連単: {int(np.average(np_tierces)):>8,} std: {np.average(np_std_tierces):>8.6f}")
        print(f"Avg 3連複: {int(np.average(np_trios)):>8,} std: {np.average(np_trios_std):>8.6f}")
        print(f"Avg 単勝 : {int(np.average(np_wins)):>8,} std: {np.average(np_wins_std):>8.6f}")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        extract_highrate(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        extract_highrate(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        print("extract_highrate.py date type(nn/lm) [rate]")
