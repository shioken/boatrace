#!/bin/bash

./predict_nn.py $1
./make_votes_nn.py $1
./inquire_nn.py $1