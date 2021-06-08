#!/usr/bin/env python3

import pandas as pd
import lightgbm as lgb
from sklearn import datasets
from sklearn.model_selection import train_test_split
import glob
import numpy as np

files = sorted(glob.glob('csv/*.csv'), reverse=True)
csvs = []

# 新しいものから1年分件取得する
# for i in range(1, 365 * 2 + 1):
for i, file in enumerate(files):
    csv = pd.read_csv(file)
    csvs.append(csv)

    if i > 365 * 2:
        break

df = pd.concat(csvs)

result = df["result"].map(lambda x: 1 if x == "01" else 2 if x == "02" else 3 if x == "03" else 4 if x == "04" else 5 if x == "05" else 6)

queries = []
cpid = -1
crno = 0
index = -1
for placeid, number in zip(df["placeid"], df["racenumber"]):
    if cpid != placeid or crno != number:
        cpid = placeid
        crno = number
        index += 1
        queries.append(1)
    else:
        queries[index] += 1

df = df.drop(["place", "racenumber", "area", "name", "age", "motor_no", "boat_no"], axis=1)

ranks = ["A1", "A2", "B1", "B2"]
for rank in ranks:
    a = df["rank"].map(lambda x: 1 if x == rank else 0)
    a.name = rank
    df = pd.concat([df, a], axis=1)
df = df.drop(["rank"], axis=1)

# columns = list(df.columns)
# columns.remove("order")

X = df.drop(["result"], axis=1)
y = result.astype(int)

print(X.head(12))

racecount = len(queries)
test_race = int(racecount * 2 / 10)
train_race = racecount - test_race

races_train_train, races_train_valid, races_target_train, races_target_train_valid = train_test_split(
    X, y, test_size=test_race * 6, shuffle=False)

queries_train = queries[:train_race]
queries_test = queries[train_race:]

print(type(X), type(y))

lgtrain = lgb.Dataset(races_train_train, races_target_train,
                      group=queries_train, categorical_feature=[0, 1])
lgvalid = lgb.Dataset(races_train_valid, races_target_train_valid,
                      group=queries_test, reference=lgtrain, categorical_feature=[0, 1])

lgbm_params = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [1, 2, 3],
    'learning_rate': 0.01,
    'min_data': 1,
    'min_data_in_bin': 1,
    # 'device': 'gpu',
}

lgb_clf = lgb.train(
    lgbm_params,
    lgtrain,
    categorical_feature=[0],
    num_boost_round=250,
    valid_sets=[lgtrain, lgvalid],
    valid_names=['train', 'valid'],
    early_stopping_rounds=20,
    verbose_eval=5
)

lgb_clf.save_model("model/lambdarank.txt")

importance = pd.DataFrame(lgb_clf.feature_importance(
    importance_type='gain'), index=races_train_train.columns, columns=['importance'])

print(importance)
