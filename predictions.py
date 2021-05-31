#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import keras
from keras import models, layers, regularizers
import numpy as np

model = None

def trimLine(line):
    return re.sub('[ ]+', ' ', re.sub(r"[\u3000]", "", line)).split(' ')

def prediction(racers, lines, race):
    X = np.array(racers)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    X -= mean
    X /= std
    X = np.nan_to_num(X)
    predictions = model.predict(X)
    sum = predictions.sum()
    mean = predictions.mean()
    std = predictions.std()

    race["sum"] = float(sum)
    race["mean"] = float(mean)
    race["std"] = float(std)

    lines.append('\n')
    lines.append("sum:{2:>.5f} mean:{0:>.5f} std:{1:>.5f}\n".format(mean, std, sum))
    for i, pr in enumerate(predictions):
        deviation = (pr[0] - mean) / std
        deviation_value = deviation * 10 + 50
        # print((i + 1), "{0:>8.3f}% {1:>8.3f}".format(pr[0] * 100, deviation_value))
        lines.append("{2} {0:>8.3f}% {1:>8.3f}\n".format(pr[0] * 100, deviation_value, i + 1))

        racer = race["racers"][i]
        racer["score"] = float(pr[0])
        racer["deviation"] = float(deviation)

RANKMAP = {
    'A1': [1.0, 0.0, 0.0, 0.0],
    'A2': [0.0, 1.0, 0.0, 0.0],
    'B1': [0.0, 0.0, 1.0, 0.0],
    'B2': [0.0, 0.0, 0.0, 1.0],
}

def parsePlayer(line):
    (number, id, name, age, area, weight, rank, win_all, sec_all, win_cur, sec_cur, motor_no, motor_ratio, boat_no, boat_ratio) = (
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
        float(line[53:59])
    )

    rank_val = RANKMAP[rank]

    X = [float(number), float(weight), win_all, sec_all, win_cur, sec_cur, motor_ratio, boat_ratio]
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
                    place = trimLine(line)[0].replace('ボートレース', '')
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
            json.dump(jroot, jf, ensure_ascii = False, indent = 4)
        



def openfile(date):
    filename = f'racelist/b{date}.txt'
    predictfile = f'predicted/p{date}.txt'
    pjsonfile = f'predicted/p{date}.json'
    if not os.path.exists(filename):
        print(f"file '{filename} is not found")
        return

    parseRacelistFile(filename, predictfile, pjsonfile)

if __name__ == '__main__':
    model = models.load_model('model/br_model.h5')
    # print(model.summary())
    if len(sys.argv) > 1:
        openfile(sys.argv[1])
