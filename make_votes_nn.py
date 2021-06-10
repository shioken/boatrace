#!/usr/bin/env python3
import glob
import re
import os
import json
import sys

def output_json(json):
    for place in json:
        # print(place["name"])
        for race in place["races"]:
            line = f"{race['number']:2}R ({race['std']:>5.3f}) "
            for v in race['votes']:
                line += f'{v} '
            line += f'{race["votewin"]}'
            # print(line)

def make_vote(pname, area=""):
    filepath = f'predicted/n{pname}.json'
    votepath = f'votes/n{pname}.json'
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
                    stds = []
                    for race in place["races"]:
                        print(race["number"], race["name"])
                        stds.append(race["std"])
                        racers = race["racers"]
                        sorted_racers = sorted(racers, key=lambda x: x["score"], reverse=True)
                        vote = []
                        for i, racer in enumerate(sorted_racers):
                            score = racer["score"]
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
                    for i, vote in enumerate(votes):
                        jr = {}
                        jr["number"] = i + 1
                        jr["std"] = stds[i]
                        jr["votes"] = []
                        jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][2]}")
                        jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][3]}")
                        jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][4]}")
                        jr["votes"].append(f"{votes[i][0]}-{votes[i][2]}-{votes[i][3]}")
                        jr["votewin"] = votes[i][0]

                        jrs.append(jr)
                    
            # print(json.dumps(all_votes, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
            # print("")
            # print("------------------------------")
            # print(pname)
            output_json(all_votes)

            with open(votepath, 'w', encoding='utf-8') as vf:
                json.dump(all_votes, vf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

    else:
        print(f'{filepath} dose not exists.')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        make_vote(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        make_vote(sys.argv[1])
    else:
        print("ファイルを指定してください")
