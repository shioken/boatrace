#!/usr/bin/env python3
import sys
import utils
import os
import re
import json
import numpy as np
import pandas as pd
from sklearn import datasets, preprocessing
from pyclustering.cluster.xmeans import xmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer

def show_deviation(date, type, tp = None, tr = -1):
    if not re.match("nn|lm", type):
        print("type not found. nn   or lm")
        return
    
    prefix = 'n' if type == 'nn' else 'l'
    pfile = f'predicted/{prefix}{date}.json'
    if not os.path.exists(pfile):
        print(f"{pfile} is not exists.")
        return

    with open(pfile, 'r', encoding='utf-8') as pf:
        pjson = json.load(pf)
        for place in pjson['places']:
            if not tp or tp == place['name']:
                # print(place['name'])
                for race in place['races']:
                    if tr < 0 or race['number'] == tr:
                        # print(f"{race['number']:2}R")
                        scores = np.array(list(map(lambda x: x['score'], race['racers'])))
                        std = np.std(scores)
                        avg = np.average(scores)

                        print(f"   std: {std:2.8f} avg: {avg:2.8f}")
                        print("")

                        df = pd.DataFrame()

                        for i, racer in enumerate(race['racers']):
                            print(f" {racer['course']} {racer['name']} {racer['score']: 2.8f} {(scores[i] - avg) / std * 10 + 50: 2.8f}")
                            df = df.append([scores[i]])

                        df = df.reset_index(drop=True)
                        # print(df)

                        X = df.copy()
                        scaler = preprocessing.StandardScaler()
                        scaler.fit(X)
                        scaled_X = scaler.transform(X)

                        # クラスタリングの初期条件
                        amount_initial_centers = 2
                        initial_centers = kmeans_plusplus_initializer(X, amount_initial_centers).initialize()

                        # クラスタリングの実行
                        xmeans_instance = xmeans(scaled_X, initial_centers=initial_centers, )
                        xmeans_instance.process()

                        # クラスタリングした要素番号を取得
                        clusters = xmeans_instance.get_clusters()

                        def avg_scores(cs):
                            sum = 0
                            for x in cs:
                                sum += df.iloc[x][0]
                            return sum / len(cs)

                        sorted_clusters = sorted(clusters, key=lambda x: avg_scores(x))
                        sorted_clusters.reverse()

                        print(f"num of clusters: {len(sorted_clusters)}")
                        for i, cluster in enumerate(sorted_clusters):
                            print(f"cluster {i}")
                            for j in cluster:
                                print(j + 1)

                        if tr > -1:
                            return scores
        
                    
        
    

if __name__ == '__main__':
    date = ""
    if len(sys.argv) > 1:
        date = sys.argv[1]
        if date == 'today':
            date = utils.getStringToday()
        elif date == 'yesterday':
            date = utils.getStringYesterday()
        elif date == 'tommorow':
            date = utils.getStringTommorow()

    if len(sys.argv) == 3:
        show_deviation(date, sys.argv[2])
    elif len(sys.argv) == 2:
        show_deviation(date, 'nn')
        show_deviation(date, 'lm')
    elif len(sys.argv) == 4:
        show_deviation(date, sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        show_deviation(date, sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        print("show_deviation.py date type(nn/lm)")
