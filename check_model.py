#!/usr/bin/env python3
import json
import glob

places = set()
placeids = set()

def checkModel(model):
    with open(model, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        for race in data:
            places.add(race["place"])
            placeids.add(race["placeid"])
            if not 'result' in race:
                print(model)
                print(f"{race['place']}, {race['racenumber']} not result")

def checkModels(models):
    for model in models:
        checkModel(model)

if __name__ == '__main__':
    models = glob.glob('model/*.json')
    checkModels(models)
    print(places, placeids)
    print(len(places), len(placeids))
