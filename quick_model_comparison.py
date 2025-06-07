#!/usr/bin/env python3
"""
高速モデル比較システム
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import glob

def load_sample_data():
    """サンプルデータを読み込み"""
    csv_files = sorted(glob.glob('csv/m*.csv'))
    
    if not csv_files:
        print("CSVファイルが見つかりません")
        return None, None
    
    # 最新の30ファイルのみ使用（高速化）
    sample_files = csv_files[-30:]
    
    dfs = []
    for file in sample_files[:10]:  # さらに10ファイルに制限
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except:
            continue
    
    if not dfs:
        return None, None
    
    data = pd.concat(dfs, ignore_index=True)
    print(f"データ数: {len(data)}")
    
    # 基本的な前処理
    data = data.dropna(subset=['result'])
    data['is_winner'] = (data['result'] == '01').astype(int)
    
    # 基本特徴量のみ使用
    features = []
    if 'number' in data.columns:
        features.append('number')
    if 'win_all' in data.columns:
        data['win_all'] = pd.to_numeric(data['win_all'], errors='coerce').fillna(0)
        features.append('win_all')
    if 'sec_all' in data.columns:
        data['sec_all'] = pd.to_numeric(data['sec_all'], errors='coerce').fillna(0)
        features.append('sec_all')
    if 'motor_ratio' in data.columns:
        data['motor_ratio'] = pd.to_numeric(data['motor_ratio'], errors='coerce').fillna(50)
        features.append('motor_ratio')
    if 'boat_ratio' in data.columns:
        data['boat_ratio'] = pd.to_numeric(data['boat_ratio'], errors='coerce').fillna(50)
        features.append('boat_ratio')
    if 'placeid' in data.columns:
        features.append('placeid')
    if 'racenumber' in data.columns:
        features.append('racenumber')
    
    if not features:
        print("使用可能な特徴量がありません")
        return None, None
    
    X = data[features].fillna(0)
    y = data['is_winner']
    
    print(f"特徴量: {features}")
    print(f"データ形状: {X.shape}")
    print(f"1着率: {y.mean():.3f}")
    
    return X, y

def compare_models(X, y):
    """モデル比較"""
    print("\nモデル学習開始...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    results = {}
    
    # 1. XGBoost
    print("XGBoost学習中...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    
    y_pred = xgb_model.predict(X_test)
    y_prob = xgb_model.predict_proba(X_test)[:, 1]
    
    results['XGBoost'] = {
        'accuracy': accuracy_score(y_test, y_pred),
        'auc': roc_auc_score(y_test, y_prob)
    }
    
    # 2. LightGBM  
    print("LightGBM学習中...")
    lgb_model = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    lgb_model.fit(X_train, y_train)
    
    y_pred = lgb_model.predict(X_test)
    y_prob = lgb_model.predict_proba(X_test)[:, 1]
    
    results['LightGBM'] = {
        'accuracy': accuracy_score(y_test, y_pred),
        'auc': roc_auc_score(y_test, y_prob)
    }
    
    # 結果表示
    print("\n=== 結果比較 ===")
    for name, metrics in results.items():
        print(f"{name}:")
        print(f"  精度: {metrics['accuracy']:.4f}")
        print(f"  AUC: {metrics['auc']:.4f}")
    
    # 最適モデル
    best_model = max(results.keys(), key=lambda k: results[k]['auc'])
    print(f"\n最優秀モデル: {best_model} (AUC: {results[best_model]['auc']:.4f})")
    
    return results

def main():
    print("高速モデル比較開始")
    
    X, y = load_sample_data()
    if X is None:
        return
    
    results = compare_models(X, y)
    
    print("\n比較完了！")

if __name__ == '__main__':
    main()