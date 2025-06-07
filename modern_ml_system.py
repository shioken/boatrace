#!/usr/bin/env python3
"""
現代的な競艇予想機械学習システム
XGBoost, LightGBM, CatBoostを比較して最適モデルを選択
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import warnings
warnings.filterwarnings('ignore')

class ModernBoatRacePredictor:
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.results = {}
        
    def load_data(self):
        """既存CSVデータを読み込み"""
        csv_files = sorted(glob.glob('csv/m*.csv'))
        
        if not csv_files:
            print("CSVファイルが見つかりません")
            return None, None
            
        print(f"データファイル数: {len(csv_files)}")
        
        # 最新の6ヶ月分のデータを使用（高速化）
        recent_files = csv_files[-180:] if len(csv_files) > 180 else csv_files[-50:]
        
        dfs = []
        for file in recent_files:
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                print(f"ファイル読み込みエラー {file}: {e}")
                continue
        
        if not dfs:
            print("有効なデータがありません")
            return None, None
            
        data = pd.concat(dfs, ignore_index=True)
        print(f"総レコード数: {len(data)}")
        
        return self.prepare_features(data)
    
    def prepare_features(self, data):
        """特徴量エンジニアリング"""
        print("特徴量エンジニアリング開始...")
        
        # 基本前処理
        data = data.dropna(subset=['result'])
        
        # ターゲット変数の作成（1着=1, それ以外=0）
        data['is_winner'] = (data['result'] == '01').astype(int)
        
        # 順位を数値に変換（ランキング学習用）
        rank_map = {'01': 1, '02': 2, '03': 3, '04': 4, '05': 5, '06': 6}
        data['rank'] = data['result'].map(rank_map).fillna(6)
        
        # 特徴量の作成
        features = []
        
        # 基本特徴量
        if 'number' in data.columns:
            features.append('number')  # コース
        if 'age' in data.columns:
            features.append('age')
        if 'weight' in data.columns:
            features.append('weight')
        
        # 成績関連
        performance_cols = ['win_all', 'sec_all', 'win_cur', 'sec_cur']
        for col in performance_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
                features.append(col)
        
        # モーター・ボート成績
        equipment_cols = ['motor_ratio', 'boat_ratio']
        for col in equipment_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(50.0)
                features.append(col)
        
        # 場・レース番号
        if 'placeid' in data.columns:
            features.append('placeid')
        if 'racenumber' in data.columns:
            features.append('racenumber')
        
        # ランクをカテゴリカル変数に
        if 'rank' in data.columns and 'rank' not in features:
            le = LabelEncoder()
            data['rank_encoded'] = le.fit_transform(data['rank'].astype(str).fillna('B1'))
            features.append('rank_encoded')
        
        # 季節成績（r1-r6）
        season_cols = [f'r{i}' for i in range(1, 7)]
        for col in season_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
                features.append(col)
        
        # 派生特徴量
        if 'win_all' in data.columns and 'sec_all' in data.columns:
            data['total_rate'] = data['win_all'] + data['sec_all']
            features.append('total_rate')
        
        if 'motor_ratio' in data.columns and 'boat_ratio' in data.columns:
            data['equipment_avg'] = (data['motor_ratio'] + data['boat_ratio']) / 2
            features.append('equipment_avg')
        
        # 年齢グループ
        if 'age' in data.columns:
            data['age_group'] = pd.cut(data['age'], bins=[0, 25, 35, 45, 100], labels=[0, 1, 2, 3])
            data['age_group'] = data['age_group'].astype(int)
            features.append('age_group')
        
        print(f"使用特徴量数: {len(features)}")
        print(f"特徴量: {features}")
        
        # 欠損値処理
        X = data[features].fillna(0)
        y = data['is_winner']
        
        print(f"最終データ形状: X={X.shape}, y={y.shape}")
        print(f"1着率: {y.mean():.3f}")
        
        return X, y
    
    def train_models(self, X, y):
        """複数のモデルを学習"""
        print("\nモデル学習開始...")
        
        # データ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"訓練データ: {X_train.shape}")
        print(f"テストデータ: {X_test.shape}")
        
        # 1. XGBoost
        print("\n1. XGBoost学習中...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,  # 500から200に削減
            max_depth=4,       # 6から4に削減
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            early_stopping_rounds=20  # 50から20に削減
        )
        
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        self.models['XGBoost'] = xgb_model
        self.feature_importance['XGBoost'] = xgb_model.feature_importances_
        
        # 2. LightGBM
        print("2. LightGBM学習中...")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=200,  # 500から200に削減
            max_depth=4,       # 6から4に削減
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        
        lgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)]  # 50から20に削減
        )
        
        self.models['LightGBM'] = lgb_model
        self.feature_importance['LightGBM'] = lgb_model.feature_importances_
        
        # 3. CatBoost
        print("3. CatBoost学習中...")
        cb_model = cb.CatBoostClassifier(
            iterations=200,  # 500から200に削減
            depth=4,         # 6から4に削減
            learning_rate=0.1,
            random_seed=42,
            verbose=False
        )
        
        cb_model.fit(
            X_train, y_train,
            eval_set=(X_test, y_test),
            early_stopping_rounds=20  # 50から20に削減
        )
        
        self.models['CatBoost'] = cb_model
        self.feature_importance['CatBoost'] = cb_model.feature_importances_
        
        # モデル評価
        self.evaluate_models(X_test, y_test)
        
        return X_train, X_test, y_train, y_test
    
    def evaluate_models(self, X_test, y_test):
        """モデル性能評価"""
        print("\n=== モデル性能評価 ===")
        
        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            logloss = log_loss(y_test, y_prob)
            auc = roc_auc_score(y_test, y_prob)
            
            self.results[name] = {
                'accuracy': accuracy,
                'logloss': logloss,
                'auc': auc
            }
            
            print(f"{name}:")
            print(f"  精度: {accuracy:.4f}")
            print(f"  LogLoss: {logloss:.4f}")
            print(f"  AUC: {auc:.4f}")
    
    def plot_feature_importance(self, X):
        """特徴量重要度の可視化"""
        plt.figure(figsize=(15, 10))
        
        for i, (name, importance) in enumerate(self.feature_importance.items()):
            plt.subplot(2, 2, i+1)
            
            feature_imp = pd.DataFrame({
                'feature': X.columns,
                'importance': importance
            }).sort_values('importance', ascending=False).head(10)
            
            sns.barplot(data=feature_imp, x='importance', y='feature')
            plt.title(f'{name} - Top 10 Features')
            plt.xlabel('Importance')
        
        plt.tight_layout()
        plt.savefig('feature_importance_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_best_model(self):
        """最高性能のモデルを選択"""
        if not self.results:
            return None
            
        # AUCスコアで比較
        best_name = max(self.results.keys(), key=lambda k: self.results[k]['auc'])
        best_model = self.models[best_name]
        
        print(f"\n最優秀モデル: {best_name}")
        print(f"AUC: {self.results[best_name]['auc']:.4f}")
        
        return best_name, best_model
    
    def predict_races(self, X, model_name=None):
        """レース予測"""
        if model_name is None:
            model_name, _ = self.get_best_model()
        
        model = self.models[model_name]
        probabilities = model.predict_proba(X)[:, 1]
        
        return probabilities

def main():
    print("現代的競艇予想システム開始")
    
    predictor = ModernBoatRacePredictor()
    
    # データ読み込み
    X, y = predictor.load_data()
    if X is None:
        return
    
    # モデル学習
    X_train, X_test, y_train, y_test = predictor.train_models(X, y)
    
    # 特徴量重要度可視化
    predictor.plot_feature_importance(X)
    
    # 最適モデル選択
    best_name, best_model = predictor.get_best_model()
    
    print(f"\n学習完了！")
    print(f"最優秀モデル: {best_name}")
    
    # モデル保存
    import joblib
    joblib.dump(best_model, f'modern_model_{best_name.lower()}.pkl')
    print(f"モデル保存: modern_model_{best_name.lower()}.pkl")

if __name__ == '__main__':
    main()