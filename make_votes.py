#!/usr/bin/env python3
import glob
import re
import os
import json
import sys
import numpy as np
import utils

def output_json(json):
    for place in json:
        # print(place["name"])
        for race in place["races"]:
            line = f"{race['number']:2}R "
            for v in race['votes']:
                line += f'{v} '

            if 'vorewin' in race:
                line += f'{race["votewin"]}'

            # print(line)

def make_vote(pname, type):
    if not re.match("nn|lm", type):
        print("type not found. nn   or lm")
        return

    prefix = 'n' if type == 'nn' else 'l'
    out_predix = 'n' if type == 'nn' else 'l'
    filepath = f'predicted/{prefix}{pname}.json'
    votepath = f'votes/{out_predix}{pname}.json'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            places = data["places"]
            all_votes = []
            for place in places:
                # print("------------------------------")
                # print(place["name"])
                # print("------------------------------")
                votes = []
                votes_win = []
                for race in place["races"]:
                    # print(race["number"], race["name"])
                    racers = race["racers"]
                    sorted_racers = sorted(racers, key=lambda x: x["score"], reverse=True)
                    scores = list(map(lambda x: x["score"], racers))
                    std = np.std(scores)
                    # print(std)
                    vote = []
                    vote_win = []
                    for i, racer in enumerate(sorted_racers):
                        score = racer["score"]
                        vote.append(racer["course"])
                        if racer['deviation'] > 55:
                            vote_win.append(racer['course'])
                    votes.append(vote)
                    votes_win.append(vote_win)

                jp = {}
                jp["name"] = place["name"]
                all_votes.append(jp)
                jrs = []
                jp["races"] = jrs
                for i, vote in enumerate(votes):
                    jr = {}
                    jr["number"] = i + 1
                    jr["votes"] = []
                    # print(i, votes)
                    if len(votes[i]) > 0:
                        # jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][2]}")
                        # jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][3]}")
                        # jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][4]}")
                        # jr["votes"].append(f"{votes[i][0]}-{votes[i][2]}-{votes[i][3]}")

                        jr["votes"].append(f"{votes[i][0]}-{votes[i][1]}-{votes[i][2]}")
                        jr["votes"].append(f"{votes[i][0]}-{votes[i][2]}-{votes[i][1]}")
                        jr["votes"].append(f"{votes[i][1]}-{votes[i][0]}-{votes[i][2]}")
                        jr["votes"].append(f"{votes[i][1]}-{votes[i][2]}-{votes[i][0]}")
                        jr["votes"].append(f"{votes[i][2]}-{votes[i][0]}-{votes[i][1]}")
                        jr["votes"].append(f"{votes[i][2]}-{votes[i][1]}-{votes[i][0]}")

                        jr["votewin"] = votes_win[i]

                    jrs.append(jr)
                    
            # print(json.dumps(all_votes, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
            # print("")
            # print("------------------------------")
            output_json(all_votes)

            with open(votepath, 'w', encoding='utf-8') as vf:
                json.dump(all_votes, vf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
                print(f"out: {votepath}")

    else:
        print(f'{filepath} dose not exists.')

if __name__ == '__main__':
    date = ""
    if len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()
        elif date == 'tommorow':
            date = utils.getStringTommorow()
    else:
        date = utils.getStringToday()

    if len(sys.argv) == 3:
        make_vote(date, sys.argv[2])
    else:
        make_vote(date, 'nn')
        make_vote(date, 'lm')
