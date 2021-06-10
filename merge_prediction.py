#!/usr/bin/env python3
import glob
import os
import sys
import json
import numpy as np

def norm_scores(scores):
    return list(map(lambda x: (x - min(scores)) / (max(scores) - min(scores)), scores))

def mergePrediction(date):
    nnfile = f"predicted/p{date}.json"
    lmfile = f"predicted/l{date}.json"

    if not os.path.exists(nnfile):
        print(f"{nnfile} is not exists")
        return

    if not os.path.exists(lmfile):
        print(f"{lmfile} is not exists")
        return


    with open(nnfile, 'r', encoding='utf-8') as nn, open(lmfile, 'r', encoding='utf-8') as lm:
        nnjson = json.load(nn)
        lmjson = json.load(lm)

        places = []

        for i, place in enumerate(nnjson["places"]):
            nn_place = nnjson["places"][i]
            lm_place = lmjson["places"][i]

            if nn_place["name"] == lm_place["name"]:
                place = {}
                place["name"] = nn_place["name"]
                places.append(place)

                nn_races = nn_place["races"]
                lm_races = lm_place["races"]

                races = []
                place["races"] = races
                for j, race in enumerate(nn_races):
                    nn_race = nn_races[j]
                    lm_race = lm_races[j]

                    race = {}
                    race["number"] = nn_race["number"]

                    nn_racers = nn_race["racers"]
                    lm_racers = lm_race["racers"]

                    racers = []
                    nn_scores = []
                    lm_scores = []
                    for k, racer in enumerate(nn_racers):
                        nn_scores.append(nn_racers[k]["score"])
                        lm_scores.append(lm_racers[k]["score"])

                    nn_norm_scores = norm_scores(nn_scores)
                    lm_norm_scores = norm_scores(lm_scores)

                    race["racers"] = racers

                    for k, racer in enumerate(nn_racers):
                        racer = {}
                        racer["course"] = k + 1
                        racer["name"] = nn_racers[k]["name"]
                        racer["score"] = (nn_norm_scores[k] + lm_norm_scores[k]) / 2
                        racers.append(racer)
                    races.append(race)
            else:
                print(f"place is not same: {nn_place['name']} - {lm_place['name']}")

        root = {}
        root["places"] = places

        mmfile = f"predicted/m{date}.json"
        with open(mmfile, 'w', encoding='utf-8') as mf:
            json.dump(root, mf, indent=2, ensure_ascii=False)
            print(f"out: {mmfile}")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        mergePrediction(sys.argv[1])
    
