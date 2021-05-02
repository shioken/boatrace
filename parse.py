#!/usr/bin/env python3
import pathlib
import glob

p_fan = pathlib.Path('fan')
fans = list(p_fan.glob('*.txt'))

for fan in fans:
    print(fan)
    with open(fan, 'r') as file:
        for l in file:
            print(l)
