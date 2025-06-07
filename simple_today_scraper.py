#!/usr/bin/env python3
"""
シンプルな今日のデータ取得（テスト用）
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime

def get_today_basic_data():
    """今日の基本的なレースデータを取得"""
    today = datetime.now().strftime("%y%m%d")
    url = f"https://boatrace.jp/owpc/pc/race/index?hd=20{today}"
    
    print(f"今日({today})のデータ取得中...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"ページタイトル: {soup.title.string if soup.title else 'なし'}")
        
        # 開催場を探す
        venues = []
        links = soup.find_all('a', href=True)
        
        venue_codes = set()
        for link in links:
            href = link.get('href', '')
            if 'raceindex' in href and 'jcd=' in href:
                venue_code = href.split('jcd=')[1].split('&')[0]
                if venue_code not in venue_codes and venue_code.isdigit():
                    venue_codes.add(venue_code)
        
        venues_map = {
            '01': '桐生', '02': '戸田', '03': '江戸川', '04': '平和島', '05': '多摩川', '06': '浜名湖',
            '07': '蒲郡', '08': '常滑', '09': '津', '10': '三国', '11': 'びわこ', '12': '住之江',
            '13': '尼崎', '14': '鳴門', '15': '丸亀', '16': '児島', '17': '宮島', '18': '徳山',
            '19': '下関', '20': '若松', '21': '芦屋', '22': '福岡', '23': '唐津', '24': '大村'
        }
        
        for code in sorted(venue_codes):
            if code in venues_map:
                venues.append({
                    'code': code,
                    'name': venues_map[code]
                })
        
        print(f"開催場: {len(venues)}場")
        for venue in venues:
            print(f"  {venue['code']}: {venue['name']}")
        
        # サンプルデータ作成（実際のスクレイピングの代わり）
        sample_races = []
        
        for venue in venues[:2]:  # 最初の2場のみテスト
            for race_no in range(1, 4):  # 1-3Rのみテスト
                race_data = {
                    'date': f"20{today}",
                    'venue': venue['name'],
                    'venue_code': venue['code'],
                    'race_no': race_no,
                    'racers': []
                }
                
                # サンプルレーサーデータ
                for boat_no in range(1, 7):
                    racer = {
                        'boat_no': boat_no,
                        'name': f'選手{boat_no}',
                        'age': 25 + boat_no,
                        'weight': 50 + boat_no,
                        'rank': ['A1', 'A2', 'B1', 'B1', 'B2', 'B2'][boat_no-1],
                        'win_rate': 3.0 + boat_no * 0.5,
                        'place_rate': 25.0 + boat_no * 2,
                        'motor_no': boat_no * 10,
                        'motor_rate': 45.0 + boat_no,
                        'boat_rate': 48.0 + boat_no,
                        'r1': str(boat_no % 6 + 1),
                        'r2': str((boat_no + 1) % 6 + 1),
                        'r3': str((boat_no + 2) % 6 + 1),
                        'r4': '0',
                        'r5': '0',
                        'r6': '0'
                    }
                    race_data['racers'].append(racer)
                
                sample_races.append(race_data)
        
        return sample_races, today
        
    except Exception as e:
        print(f"エラー: {e}")
        return [], today

def main():
    races, date = get_today_basic_data()
    
    if races:
        # CSV形式で保存
        csv_data = []
        for race in races:
            for racer in race['racers']:
                row = {
                    'date': race['date'],
                    'venue': race['venue'],
                    'venue_code': race['venue_code'],
                    'race_no': race['race_no'],
                    'number': racer['boat_no'],
                    'name': racer['name'],
                    'age': racer['age'],
                    'weight': racer['weight'],
                    'rank': racer['rank'],
                    'win_all': racer['win_rate'],
                    'sec_all': racer['place_rate'],
                    'motor_ratio': racer['motor_rate'],
                    'boat_ratio': racer['boat_rate'],
                    'placeid': int(racer.get('venue_code', race['venue_code'])),
                    'racenumber': race['race_no'],
                    'r1': racer['r1'],
                    'r2': racer['r2'],
                    'r3': racer['r3'],
                    'r4': racer['r4'],
                    'r5': racer['r5'],
                    'r6': racer['r6'],
                    'result': ''  # 結果は後で取得
                }
                csv_data.append(row)
        
        # 保存
        import os
        os.makedirs("latest_data", exist_ok=True)
        
        csv_file = f"latest_data/today_sample_{date}.csv"
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\nサンプルデータ作成完了:")
        print(f"  ファイル: {csv_file}")
        print(f"  レース数: {len(races)}")
        print(f"  レコード数: {len(csv_data)}")
        
        return csv_file
    
    else:
        print("データ取得に失敗しました")
        return None

if __name__ == '__main__':
    main()