#!/usr/bin/env python3
import json
import glob

def convertFile(file):
    print(file)

def convertFiles(files):
    for file in files:
        convertFile(file)

if __name__ == '__main__':
    # files = glob.glob('model/*.json')
    files = ['models/m210525.json']
    convertFiles(files)
