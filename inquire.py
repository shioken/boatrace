#!/usr/bin/env python3
import glob
import re
import os
import json
import sys

def inquire(target):
    votefile = f'votes/v{target}.json'
    resultfile = f'json/m{target}.json'
    
    if not os.path.exists(votefile):
        print(f'{votefile} is not exists')
        return
    
    if not os.path.exists(resultfile):
        print(f'{resultfile} is not exists')
        return

if __name__ == '__main__':
    if len(sys.argv) == 2:
        inquire(sys.argv[1])
    else:
        print("Please specify a file.")
