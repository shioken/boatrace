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
import lightgbm as lgb
import utils

model_nn = None
model_lm = None

def prediction_nn(racers, race):
    global model_nn
    if model_nn is None:
        model_nn = models.load_model('model/br_model_0608.h5')
    X = np.array(racers)
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    X -= mean
    X /= std
    X = np.nan_to_num(X)
    predictions = model_nn.predict(X)
    sum = predictions.sum()
    mean = predictions.mean()
    std = predictions.std()

    race["sum"] = float(sum)
    race["mean"] = float(mean)
    race["std"] = float(std)

    norm_scores = list(map(lambda x: (x - min(predictions)) / (max(predictions) - min(predictions)), predictions))

    # lines.append('\n')
    # lines.append("sum:{2:>.5f} mean:{0:>.5f} std:{1:>.5f}\n".format(mean, std, sum))
    for i, pr in enumerate(predictions):
        deviation = (pr[0] - mean) / std
        deviation_value = deviation * 10 + 50
        # print((i + 1), "{0:>8.3f}% {1:>8.3f}".format(pr[0] * 100, deviation_value))
        # lines.append("{2} {0:>8.3f}% {1:>8.3f}\n".format(pr[0] * 100, deviation_value, i + 1))

        racer = race["racers"][i]
        racer["norm_score"] = float(norm_scores[i])
        racer["score"] = float(pr)
        racer["deviation"] = float(deviation)


def prediction_lm(racers, race):
    global model_lm
    if model_lm is None:
        model_lm = lgb.Booster(model_file='model/lambdarank.txt')

    X = np.array(racers)
    predictions = model_lm.predict(
        X, num_iteration=model_lm.best_iteration)

    norm_scores = list(map(lambda x: (x - min(predictions)) /
                       (max(predictions) - min(predictions)), predictions))

    for i, pr in enumerate(predictions):
        racer = race["racers"][i]
        racer["norm_score"] = float(norm_scores[i])
        racer["score"] = float(pr)

def makeX(racer, place, prefix):
    (number, name, age, area, weight, rank, win_all, sec_all, win_cur, sec_cur, motor_no, motor_ratio, boat_no, boat_ratio, season_result) = (
        racer["number"],
        racer["name"],
        racer["age"],
        racer["area"],
        racer["weight"],
        racer["rank"],
        racer["win_all"],
        racer["sec_all"],
        racer["win_cur"],
        racer["sec_cur"],
        racer["motor_no"],
        racer["motor_ratio"],
        racer["boat_no"],
        racer["boat_ratio"],
        [racer["r1"], racer["r2"], racer["r3"], racer["r4"], racer["r5"], racer["r6"]],
    )

    season_result = ''.join(season_result)

    placeid = places[place]

    rank_val = RANKMAP[rank]

    if prefix == 'n':
        X = [float(number), float(weight), win_all, sec_all,
             win_cur, sec_cur, motor_ratio, boat_ratio]
    else:
        X = [float(placeid), float(number), float(weight), win_all,
             sec_all, win_cur, sec_cur, motor_ratio, boat_ratio]
        season_result = re.sub(r"[ FLSK]", "0", season_result)
        for i in range(6):
            X += [float(season_result[i: i + 1])]

    X += rank_val
    return X


def prediction(date, type):
    racefile = f'json/m{date}.json'
    prefix = 'n' if type == 'nn' else 'l'
    predictfile = f'predicted/{prefix}{date}.json'

    if not os.path.exists(racefile):
        print(f"file '{racefile}' is not exists")
        return
    
    with open(racefile, 'r', encoding='utf-8') as rf:
        races = json.load(rf)

        places = []
        current_place = None
        current_place_name = None
        for race in races:
            placename = race['place']
            if placename != current_place_name:
                current_place = {}
                current_place["name"] = placename
                places.append(current_place)
                current_place_name = placename

                current_place["races"] = []
            
            jrace = {}
            current_place["races"].append(jrace)
            jrace["number"] = race["racenumber"]
            jrace["racers"] = []

            racers_X = []
            for i, racer in enumerate(race["racers"]):
                racers_X.append(makeX(racer, placename, prefix))
                jracer = {}
                jracer["name"] = racer["name"]
                jracer["course"] = i + 1
                jrace["racers"].append(jracer)

            if prefix == 'n':
                prediction_nn(racers_X, jrace)
            else:
                prediction_lm(racers_X, jrace)


        jroot = {"places": places}
        # print(json.dumps(jroot, indent=2, ensure_ascii=False))
        with open(predictfile, 'w', encoding='utf-8') as pf:
            json.dump(jroot, pf, indent=2, ensure_ascii=False)
            print(f"out: {predictfile}")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        prediction(sys.argv[1], sys.argv[2])
    else:
        print("predict.py date type([nn|lm])")
