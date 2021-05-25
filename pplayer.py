#!/usr/bin/env python3
import glob
import re

players = set()

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
    wincount = newline[offset: offset + 3]
    offset += 3
    secondcount = newline[offset: offset + 3]
    offset += 3
    racecount = newline[offset: offset + 3]
    offset += 3
    champrace = newline[offset: offset + 2]
    offset += 2
    champcount = newline[offset: offset + 2]
    offset += 2
    avgstart = newline[offset: offset + 3]
    
    offset = 142
    preiod_from = newline[offset: offset + 8]
    offset += 8
    preiod_to = newline[offset: offset + 8]
    print(number, name, shibu, rank, blood, winrate, multirate, preiod_from, preiod_to)



    # if number in players:
    #     print(f"{number}: 存在")
    
    players.add(number)

def parseFile():
    # fanfiles = glob.glob('fan/fan*.txt')
    fanfiles = ['fan/fan2010.txt']
    lines = 0

    for fanfile in fanfiles:
        print(fanfile)
        with open(fanfile, 'r') as file:
            while True:
                line = file.readline()
                if line:
                    parseLine(line)
                    lines += 1
                else:
                    break

    print(lines, len(players))

if __name__ == '__main__':
    parseFile()
