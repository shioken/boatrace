#!/usr/bin/env python3

import pandas as pd
import lightgbm as lgb
from sklearn import datasets
from sklearn.model_selection import train_test_split
import glob
import numpy as np
import os
import json
import sys
import util

# with open('model/lambdarank.txt', 'r', encoding='utf-8') as lr:
#     model_txt = lr.read()

model = None    


def prediction(racers, lines, race):
    X = np.array(racers)
    predictions = model.predict(
        X, num_iteration=model.best_iteration)

    for i, pr in enumerate(predictions):
        print(f"{(i + 1)} {pr:>10.8f}")

        racer = race["racers"][i]
        racer["score"] = float(pr)


RANKMAP = {
    'A1': [1.0, 0.0, 0.0, 0.0],
    'A2': [0.0, 1.0, 0.0, 0.0],
    'B1': [0.0, 0.0, 1.0, 0.0],
    'B2': [0.0, 0.0, 0.0, 1.0],
}


def parsePlayer(line):
    (number, id, name, age, area, weight, rank, win_all, sec_all, win_cur, sec_cur, motor_no, motor_ratio, boat_no, boat_ratio, season_result) = (
        float(line[:1]),
        line[2:6],
        line[6:10],
        int(line[10:12]),
        line[12:14],
        int(line[14:16]),
        line[16:18],
        float(line[18:24]),
        float(line[24:30]),
        float(line[30:35]),
        float(line[35:41]),
        int(line[41:44]),
        float(line[44:50]),
        int(line[50:53]),
        float(line[53:59]),
        line[60:66],
    )

    rank_val = RANKMAP[rank]

    X = [float(number), float(weight), win_all, sec_all,
         win_cur, sec_cur, motor_ratio, boat_ratio]

    # season_result = re.sub(r"[ FLSK]", "0", season_result)
    # for i in range(6):
    #     X += [float(season_result[i: i + 1])]

    X += rank_val

    return X


def parseRacelistFile(filename, pfilename, jsonfile):
    prevLine = ''
    nt = False
    place = ""
    lb = 0  # Line Break Flag '---'
    place = ''
    pline = False
    pcount = 0
    racers = []
    olines = []

    jroot = {}
    places = []
    races = []
    currace = {}
    curplace = {}
    jroot["places"] = places
    racecount = 0

    with open(filename, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()
            if line:
                if nt:
                    olines.append(line)
                    olines.append('\n')
                    place = util.trimLine(line)[0].replace('ボートレース', '')
                    curplace = {}
                    curplace["name"] = place
                    races = []
                    racecount = 0
                    curplace["races"] = races
                    places.append(curplace)
                    nt = False
                elif pline:
                    sl = line.strip()
                    olines.append(sl)
                    olines.append('\n')
                    racer = parsePlayer(line)
                    pcount += 1
                    racers.append(racer)
                    jracer = {}
                    jracer["name"] = line[6:10]
                    jracer["course"] = pcount
                    currace["racers"].append(jracer)
                    if pcount == 6:
                        prediction(racers, olines, currace)
                        pline = False
                        olines.append('\n')
                else:
                    if 'BGN' in line:
                        nt = True
                    elif 'END' in line:
                        nt = False
                    elif '---' in line:
                        lb += 1
                        if lb == 1:
                            olines.append(
                                "-------------------------------------------------------------------------------\n")
                            olines.append(f'{place} {prevLine.strip()}\n')
                            olines.append(
                                "-------------------------------------------------------------------------------\n")
                            racers = []

                            currace = {}
                            currace["name"] = prevLine.strip()
                            racecount += 1
                            currace["number"] = racecount
                            races.append(currace)
                            currace["racers"] = []

                        else:
                            # 次の行から選手が出てくる
                            lb = 0
                            pline = True
                            pcount = 0

                prevLine = line
            else:
                break

        with open(pfilename, 'w', encoding='utf-8') as pf:
            pf.writelines(olines)

        with open(jsonfile, 'w', encoding='utf-8') as jf:
            json.dump(jroot, jf, ensure_ascii=False, indent=4)


def openfile(date):
    filename = f'racelist/b{date}.txt'
    predictfile = f'predicted/l{date}.txt'
    pjsonfile = f'predicted/l{date}.json'
    if not os.path.exists(filename):
        print(f"file '{filename} is not found")
        return

    parseRacelistFile(filename, predictfile, pjsonfile)


if __name__ == '__main__':
    model = lgb.Booster(model_file='model/lambdarank.txt')
    if len(sys.argv) > 1:
        openfile(sys.argv[1])
