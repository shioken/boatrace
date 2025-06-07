#!/usr/bin/env python3

import pandas as pd
import lightgbm as lgb
from sklearn import datasets
from sklearn.model_selection import train_test_split
import glob
import numpy as np

files_2021 = glob.glob('csv/m210[1-5]*.csv')
files_2020 = glob.glob('csv/m20*.csv')
files_2019 = glob.glob('csv/m19*.csv')
files_2018 = glob.glob('csv/m18*.csv')
files = sorted(files_2018 + files_2019 + files_2020 + files_2021, reverse=True)

# files = sorted(glob.glob('csv/*.csv'), reverse=True)[4:]
csvs = []

# 新しいものから2年分件取得する
for i, file in enumerate(files):
    csv = pd.read_csv(file)
    csvs.append(csv)

    if i > 365 * 2:
        break

df = pd.concat(csvs)

df["result"] = df["result"].map(lambda x: 1 if x == "01" else 2 if x == "02" else 3 if x == "03" else 4 if x == "04" else 5 if x == "05" else 6)
df["result"] = df["result"].max() - df["result"] + 1
result = df["result"]

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

df = df.drop(["place", "area", "name", "age", "motor_no", "boat_no"], axis=1)

ranks = ["A1", "A2", "B1", "B2"]
a = df["rank"].map(lambda x: ranks.index(x))
df = df.drop(["rank"], axis=1)
a.name = "rank"
df = pd.concat([df, a], axis=1)

X = df.drop(["result"], axis=1)
y = result.astype(int)

print(X.head(12))

# データ分割を正しく実装
racecount = len(queries)
test_race = int(racecount * 0.2)  # 20%をテスト用
train_race = racecount - test_race

# レース単位でのデータ分割
train_samples = sum(queries[:train_race])
test_samples = sum(queries[train_race:])

races_train_train = X[:train_samples]
races_train_valid = X[train_samples:]
races_target_train = y[:train_samples]
races_target_train_valid = y[train_samples:]

queries_train = queries[:train_race]
queries_test = queries[train_race:]

print(type(X), type(y))

categorical_feature = ["placeid", "number", "racenumber", "rank"]
lgtrain = lgb.Dataset(races_train_train, races_target_train,
                      group=queries_train, categorical_feature=categorical_feature)  # number, rank
lgvalid = lgb.Dataset(races_train_valid, races_target_train_valid,
                      group=queries_test, reference=lgtrain, categorical_feature=categorical_feature)    # number, rank

lgbm_params = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [1, 2, 3],
    'learning_rate': 0.02,  # 0.005から0.02に増加
    'min_data': 1,
    'min_data_in_bin': 1,
    'num_leaves': 31,
    'max_depth': 6,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_child_samples': 20,
    'reg_alpha': 0.1,
    'reg_lambda': 0.1,
    # 'device': 'gpu',
}

lgb_clf = lgb.train(
    lgbm_params,
    lgtrain,
    num_boost_round=1000,  # 250から1000に増加
    valid_sets=[lgtrain, lgvalid],
    valid_names=['train', 'valid'],
    callbacks=[
        lgb.early_stopping(50),  # 20から50に増加
        lgb.log_evaluation(20)
    ]
)

lgb_clf.save_model("model/lambdarank.txt")

importance = pd.DataFrame(lgb_clf.feature_importance(
    importance_type='gain'), index=races_train_train.columns, columns=['importance'])

print(importance)
