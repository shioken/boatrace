#!/bin/bash

./predictions.py $1
./make_votes.py $1
./inquire.py $1