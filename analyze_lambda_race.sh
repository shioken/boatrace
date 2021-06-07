#!/bin/bash

./predict_lambdarank.py $1
./make_lambdarank.py $1
./inquire_lambdarank.py $1