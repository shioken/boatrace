#!/usr/bin/env python3
import glob
import re
import json

players = {}

def parseLine(line):
    number = line[:4]
    offset = 4
    name = line[offset: offset + 8]

    # Shift-JIS -> UTF-8変換時に半角カナの濁点が一文字に変換されているので文字数が合わない
    newline = line[offset:]

    p = re.compile('[\u30A1-\u30FF]+ ')
    while True:
        result = p.search(newline)
        if result:
            newline = newline[result.end():]
        else:
            break

    newline = newline.lstrip(' ')

    offset = 0
    shibu = newline[offset: offset + 2]
    offset += 2
    rank = newline[offset: offset + 2]
    offset += 2

    offset = 19
    blood = newline[offset: offset + 2]
    offset += 2
    winrate = newline[offset: offset + 4]
    offset += 4
    multirate = newline[offset: offset + 4]
    offset += 4
    wincount = int(newline[offset: offset + 3])
    offset += 3
    secondcount = int(newline[offset: offset + 3])
    offset += 3
    racecount = int(newline[offset: offset + 3])
    offset += 3
    champrace = int(newline[offset: offset + 2])
    offset += 2
    champcount = int(newline[offset: offset + 2])
    offset += 2
    avgstart = newline[offset: offset + 3]
    
    offset = 142
    preiod_from = int(newline[offset: offset + 8])
    offset += 8
    preiod_to = int(newline[offset: offset + 8])

    # 文字列 → 数値
    winrate_val = float(f'{winrate[:2]}.{winrate[2:]}')
    multirate_val = float(f'{multirate[:2]}.{multirate[2:]}')
    avgstart_val = float(f'{avgstart[:2]}.{avgstart[2:]}')

    # print(number, name, shibu, rank, blood, winrate_val, multirate_val, avgstart_val, preiod_from, preiod_to)

    obj = {}
    # obj['shibu'] = shibu
    obj['rank'] = rank
    obj['winrate'] = winrate_val
    obj['multirate'] = multirate_val
    obj['wincount'] = wincount
    obj['secondcount'] = secondcount
    obj['racecount'] = racecount
    obj['champrace'] = champrace
    obj['champcount'] = champcount
    obj['avgstart'] = avgstart_val
    obj['from'] = preiod_from
    obj['to'] = preiod_to

    if not number in players:
        players[number] = []
    players[number].append(obj)

def parseFile():
    fanfiles = glob.glob('fan/fan*.txt')
    # fanfiles = ['fan/fan2010.txt', 'fan/fan2004.txt']
    lines = 0

    for fanfile in fanfiles:
        with open(fanfile, 'r') as file:
            while True:
                line = file.readline()
                line = line.strip()
                if line:
                    parseLine(line)
                    lines += 1
                else:
                    break

    # print(lines, len(players))
    print(json.dumps(players))

if __name__ == '__main__':
    parseFile()
