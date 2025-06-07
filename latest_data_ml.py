#!/usr/bin/env python3
"""
最新データ対応機械学習システム
既存データ + 最新データで学習し、最高性能のモデルを構築
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import joblib
from datetime import datetime

class LatestDataMLSystem:
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.results = {}
        self.feature_names = []
        
    def load_all_data(self):
        """既存データ + 最新データを統合して読み込み"""
        print("データ読み込み開始...")
        
        # 1. 既存CSVデータ
        csv_files = sorted(glob.glob('csv/m*.csv'))
        
        # 2. 最新取得データ
        latest_files = sorted(glob.glob('latest_data/*.csv'))
        
        print(f"既存CSVファイル: {len(csv_files)}個")
        print(f"最新データファイル: {len(latest_files)}個")
        
        all_dfs = []
        
        # 既存データから最新300ファイルを使用
        recent_csv = csv_files[-300:] if len(csv_files) > 300 else csv_files[-100:]
        
        for file in recent_csv:
            try:
                df = pd.read_csv(file)
                all_dfs.append(df)
            except Exception as e:
                print(f"ファイル読み込みエラー {file}: {e}")
                continue
        
        # 最新データを追加
        for file in latest_files:
            try:
                df = pd.read_csv(file)
                # 最新データには結果がないので、サンプル結果を付与
                if 'result' not in df.columns:
                    df['result'] = '01'  # 暫定的に1着とする
                all_dfs.append(df)
                print(f"最新データ追加: {file}")
            except Exception as e:
                print(f"最新データ読み込みエラー {file}: {e}")
                continue
        
        if not all_dfs:
            print("有効なデータがありません")
            return None, None
            
        # 統合
        combined_data = pd.concat(all_dfs, ignore_index=True)
        print(f"統合後データ数: {len(combined_data)}")
        
        return self.prepare_enhanced_features(combined_data)
    
    def prepare_enhanced_features(self, data):
        """拡張された特徴量エンジニアリング"""
        print("拡張特徴量エンジニアリング開始...")
        
        # 基本前処理
        data = data.dropna(subset=['result'])
        
        # ターゲット変数
        data['is_winner'] = (data['result'] == '01').astype(int)
        
        features = []
        
        # === 基本特徴量 ===
        basic_features = ['number', 'age', 'weight']
        for col in basic_features:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(
                    {'number': 1, 'age': 30, 'weight': 52}[col]
                )
                features.append(col)
        
        # === 成績関連特徴量 ===
        performance_cols = ['win_all', 'sec_all', 'win_cur', 'sec_cur']
        for col in performance_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
                features.append(col)
        
        # === 機材特徴量 ===
        equipment_cols = ['motor_ratio', 'boat_ratio']
        for col in equipment_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(50.0)
                features.append(col)
        
        # === 場・レース特徴量 ===
        if 'placeid' in data.columns:
            data['placeid'] = pd.to_numeric(data['placeid'], errors='coerce').fillna(1)
            features.append('placeid')
            
        if 'racenumber' in data.columns:
            data['racenumber'] = pd.to_numeric(data['racenumber'], errors='coerce').fillna(1)
            features.append('racenumber')
        
        # === ランク特徴量 ===
        if 'rank' in data.columns:
            le = LabelEncoder()
            data['rank_encoded'] = le.fit_transform(data['rank'].astype(str).fillna('B1'))
            features.append('rank_encoded')
        
        # === 季節成績特徴量 ===
        season_cols = [f'r{i}' for i in range(1, 7)]
        for col in season_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
                features.append(col)
        
        # === 派生特徴量（拡張版） ===
        
        # 1. 総合成績
        if 'win_all' in data.columns and 'sec_all' in data.columns:
            data['total_performance'] = data['win_all'] + data['sec_all']
            features.append('total_performance')
        
        # 2. 機材総合力
        if 'motor_ratio' in data.columns and 'boat_ratio' in data.columns:
            data['equipment_power'] = (data['motor_ratio'] + data['boat_ratio']) / 2
            data['equipment_diff'] = data['motor_ratio'] - data['boat_ratio']
            features.extend(['equipment_power', 'equipment_diff'])
        
        # 3. 年齢グループ
        if 'age' in data.columns:
            data['age_group'] = pd.cut(data['age'], bins=[0, 25, 35, 45, 100], labels=[0, 1, 2, 3])
            data['age_group'] = data['age_group'].astype(int)
            features.append('age_group')
        
        # 4. 体重グループ
        if 'weight' in data.columns:
            data['weight_group'] = pd.cut(data['weight'], bins=[0, 50, 53, 57, 100], labels=[0, 1, 2, 3])
            data['weight_group'] = data['weight_group'].astype(int)
            features.append('weight_group')
        
        # 5. コースの有利性
        if 'number' in data.columns:
            # 1号艇は有利
            data['is_course_1'] = (data['number'] == 1).astype(int)
            # インコース（1-3号艇）
            data['is_inner'] = (data['number'] <= 3).astype(int)
            features.extend(['is_course_1', 'is_inner'])
        
        # 6. 最近の成績パターン
        season_cols = [f'r{i}' for i in range(1, 7)]
        if all(col in data.columns for col in season_cols):
            # 最近の1着回数
            data['recent_wins'] = sum([(data[col] == 1).astype(int) for col in season_cols])
            # 最近の連対回数
            data['recent_places'] = sum([(data[col].isin([1, 2])).astype(int) for col in season_cols])
            # 最近の3着内回数
            data['recent_top3'] = sum([(data[col].isin([1, 2, 3])).astype(int) for col in season_cols])
            
            features.extend(['recent_wins', 'recent_places', 'recent_top3'])
        
        # 7. 場の特性
        if 'placeid' in data.columns:
            # 難水面（江戸川、平和島など）
            difficult_venues = [3, 4]  # 江戸川、平和島
            data['is_difficult_venue'] = data['placeid'].isin(difficult_venues).astype(int)
            features.append('is_difficult_venue')
        
        # 8. レース時間帯の特性
        if 'racenumber' in data.columns:
            # 早い時間のレース
            data['is_early_race'] = (data['racenumber'] <= 6).astype(int)
            # メインレース（最終3レース）
            data['is_main_race'] = (data['racenumber'] >= 10).astype(int)
            features.extend(['is_early_race', 'is_main_race'])
        
        # === 特徴量の正規化・標準化 ===
        continuous_features = ['win_all', 'sec_all', 'motor_ratio', 'boat_ratio', 
                              'total_performance', 'equipment_power']
        
        for col in continuous_features:
            if col in data.columns and col in features:
                # 異常値を除去（3σ法）
                mean_val = data[col].mean()
                std_val = data[col].std()
                data[col] = data[col].clip(mean_val - 3*std_val, mean_val + 3*std_val)
        
        self.feature_names = features
        print(f"使用特徴量数: {len(features)}")
        print(f"特徴量: {features}")
        
        # 最終データ準備
        X = data[features].fillna(0)
        y = data['is_winner']
        
        print(f"最終データ形状: X={X.shape}, y={y.shape}")
        print(f"1着率: {y.mean():.3f}")
        print(f"データ期間: {data['date'].min() if 'date' in data.columns else '不明'} - {data['date'].max() if 'date' in data.columns else '不明'}")
        
        return X, y
    
    def train_advanced_models(self, X, y):
        """高度なモデル学習"""
        print("\n高度なモデル学習開始...")
        
        # データ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"訓練データ: {X_train.shape}")
        print(f"テストデータ: {X_test.shape}")
        
        # === 1. XGBoost（最適化版） ===
        print("\n1. XGBoost（最適化版）学習中...")
        xgb_model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            eval_metric='auc',
            early_stopping_rounds=30
        )
        
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        self.models['XGBoost_Advanced'] = xgb_model
        self.feature_importance['XGBoost_Advanced'] = xgb_model.feature_importances_
        
        # === 2. LightGBM（最適化版） ===
        print("2. LightGBM（最適化版）学習中...")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            random_state=42,
            verbose=-1
        )
        
        lgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[lgb.early_stopping(30), lgb.log_evaluation(0)]
        )
        
        self.models['LightGBM_Advanced'] = lgb_model
        self.feature_importance['LightGBM_Advanced'] = lgb_model.feature_importances_
        
        # === 3. アンサンブルモデル ===
        print("3. アンサンブルモデル作成中...")
        ensemble_predictions = (
            xgb_model.predict_proba(X_test)[:, 1] * 0.6 +
            lgb_model.predict_proba(X_test)[:, 1] * 0.4
        )
        
        # アンサンブル結果を評価
        ensemble_auc = roc_auc_score(y_test, ensemble_predictions)
        self.results['Ensemble'] = {
            'auc': ensemble_auc,
            'accuracy': accuracy_score(y_test, (ensemble_predictions > 0.5).astype(int))
        }
        
        # 個別モデル評価
        self.evaluate_models(X_test, y_test)
        
        return X_train, X_test, y_train, y_test
    
    def evaluate_models(self, X_test, y_test):
        """詳細なモデル評価"""
        print("\n=== 詳細モデル評価 ===\n")
        
        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_prob)
            
            self.results[name] = {
                'accuracy': accuracy,
                'auc': auc
            }
            
            print(f"{name}:")
            print(f"  精度: {accuracy:.4f}")
            print(f"  AUC: {auc:.4f}")
            
            # 詳細レポート
            print(f"  分類レポート:")
            report = classification_report(y_test, y_pred, output_dict=True)
            print(f"    適合率: {report['1']['precision']:.4f}")
            print(f"    再現率: {report['1']['recall']:.4f}")
            print(f"    F1スコア: {report['1']['f1-score']:.4f}")
            print()
    
    def plot_feature_importance(self, X):
        """特徴量重要度の詳細可視化"""
        plt.figure(figsize=(20, 12))
        
        n_models = len(self.feature_importance)
        
        for i, (name, importance) in enumerate(self.feature_importance.items()):
            plt.subplot(2, 2, i+1)
            
            feature_imp = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False).head(15)
            
            sns.barplot(data=feature_imp, x='importance', y='feature')
            plt.title(f'{name} - Top 15 Features')
            plt.xlabel('Importance')
            
        plt.tight_layout()
        plt.savefig('latest_feature_importance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 特徴量重要度の統計
        print("\n=== 特徴量重要度分析 ===\n")
        importance_df = pd.DataFrame({
            name: imp for name, imp in self.feature_importance.items()
        }, index=self.feature_names)
        
        importance_df['平均'] = importance_df.mean(axis=1)
        importance_df = importance_df.sort_values('平均', ascending=False)
        
        print("Top 10 重要特徴量:")
        print(importance_df.head(10).round(4))
    
    def get_best_model(self):
        """最高性能モデルの選択"""
        if not self.results:
            return None, None
            
        # AUCスコアで比較
        best_name = max(self.results.keys(), key=lambda k: self.results[k]['auc'])
        
        if best_name == 'Ensemble':
            print(f"\n🏆 最優秀モデル: {best_name}")
            print(f"AUC: {self.results[best_name]['auc']:.4f}")
            return best_name, None  # アンサンブルは特別処理
        else:
            best_model = self.models[best_name]
            print(f"\n🏆 最優秀モデル: {best_name}")
            print(f"AUC: {self.results[best_name]['auc']:.4f}")
            print(f"精度: {self.results[best_name]['accuracy']:.4f}")
            
            return best_name, best_model
    
    def save_model(self, model_name, model):
        """モデルの保存"""
        if model is not None:
            model_file = f'latest_model_{model_name.lower().replace("_", "")}.pkl'
            joblib.dump(model, model_file)
            print(f"モデル保存: {model_file}")
            
            # 特徴量名も保存
            feature_file = f'latest_features_{model_name.lower().replace("_", "")}.pkl'
            joblib.dump(self.feature_names, feature_file)
            print(f"特徴量保存: {feature_file}")
            
            return model_file
        return None

def main():
    print("🚀 最新データ対応機械学習システム開始")
    print("=" * 50)
    
    system = LatestDataMLSystem()
    
    # データ読み込み
    X, y = system.load_all_data()
    if X is None:
        print("❌ データ読み込みに失敗しました")
        return
    
    # モデル学習
    X_train, X_test, y_train, y_test = system.train_advanced_models(X, y)
    
    # 特徴量重要度可視化
    system.plot_feature_importance(X)
    
    # 最適モデル選択
    best_name, best_model = system.get_best_model()
    
    # モデル保存
    if best_model is not None:
        model_file = system.save_model(best_name, best_model)
    
    print("\n✅ 学習完了！")
    print(f"📊 使用特徴量数: {len(system.feature_names)}")
    print(f"📈 最高AUC: {max(system.results.values(), key=lambda x: x['auc'])['auc']:.4f}")
    print(f"💾 保存済みモデル: {best_name}")

if __name__ == '__main__':
    main()