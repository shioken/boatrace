#!/bin/bash

./prediction.py $1
./make_vote.py $1
./inquire.py $1