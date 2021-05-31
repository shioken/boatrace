#!/usr/bin/env python3
import glob
import re
import os
import json
import sys

def output_json(json):
    for place in json:
        print(place["name"])
        for race in place["races"]:
            print(f"{race['number']:2}R {race['vote']}")
def predictit(pname, area=""):
    filepath = f'predicted/p{pname}.json'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            places = data["places"]
            all_votes = []
            for place in places:
                if len(area) == 0 or area == place["name"]:
                    print("------------------------------")
                    print(place["name"])
                    print("------------------------------")
                    votes = []
                    for race in place["races"]:
                        print(race["number"], race["name"])
                        racers = race["racers"]
                        sorted_racers = sorted(racers, key=lambda x: x["score"], reverse=True)
                        vote = []
                        for i, racer in enumerate(sorted_racers):
                            score = racer["score"]
                            if i < 3:
                                vote.append(racer["course"])
                            print(racer["course"], racer["name"], f"{score * 100:>8.3f}%", f"{1 / score:>8.3f}")
                        print("")
                        votes.append(vote)
                    
                    print(place["name"])
                    jp = {}
                    jp["name"] = place["name"]
                    all_votes.append(jp)
                    jrs = []
                    jp["races"] = jrs
                    for i in range(12):
                        jr = {}
                        jr["number"] = i + 1
                        jr["vote"] = f"{votes[i][0]}-{votes[i][1]}-{votes[i][2]}"
                        jrs.append(jr)
                        print(
                            f"{i + 1:>2}R {votes[i][0]}-{votes[i][1]}-{votes[i][2]}")
                    
                # print(json.dumps(all_votes, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
                output_json(all_votes)

    else:
        print(f'{filepath} dose not exists.')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        predictit(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        predictit(sys.argv[1])
    else:
        print("ファイルを指定してください")
