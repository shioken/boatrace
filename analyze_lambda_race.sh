#!/bin/bash

./predict_lambdarank.py $1
./make_votes_lambdarank.py $1
./inquire_lambdarank.py $1