#!/usr/bin/env python3
import predict_lambdarank as pl
import make_votes_lambdarank as mvl
import inquire_lambdarank as inquire
import datetime
import sys


def agreegate(target, days = 31):
    date = datetime.date(2000 + int(target[:2]), int(target[2:4]), int(target[4:]))

    all_race_count = 0
    all_bet_race = 0
    all_bet = 0
    all_tierce_count = 0
    all_tierce_inquire = 0
    all_trio_count = 0
    all_trio_inquire = 0
    all_tierce_one_count = 0
    all_tierce_one_inquire = 0
    all_win_count = 0
    all_win_inquire = 0


    dur = 0
    while dur < days:
        target = date.strftime("%y%m%d")

        pl.openfile(target)
        mvl.make_vote(target)

        result = inquire.inquire(target)
        if result:
            (total_race, total_bet_race, total_bet, tierce_count, tierce_inquire, trio_count,
             trio_inquire, tierce_one_count, tierce_one_inquire, win_count, win_inquire) = result

            all_race_count += total_race
            all_bet_race += total_bet_race
            all_bet += total_bet
            all_tierce_count += tierce_count
            all_tierce_inquire += tierce_inquire
            all_trio_count += trio_count
            all_trio_inquire += trio_inquire
            all_tierce_one_count += tierce_one_count
            all_tierce_one_inquire += tierce_one_inquire
            all_win_count += win_count
            all_win_inquire += win_inquire

            
        date = date + datetime.timedelta(days=1)
        dur += 1
    
    print("")
    print(f"総レース数: {all_race_count:>5} 参加レース数: {all_bet_race:>5} 参加率: {all_bet_race / all_race_count * 100:>6.2f}%")
    print(f"総投資額: 3連単x4 {all_bet:>8,} 3連単x1 {all_bet_race * 100:>8,} 3連複x4 {all_bet:>8,} 単勝 {all_bet_race * 100:>8,}")
    print(f"相当選率: 3連単x4 {all_tierce_count / all_bet_race * 100:>7.2f}% 3連単x1 {all_tierce_one_count / all_bet_race * 100:>7.2f}% 3連複x4 {all_trio_count / all_bet_race * 100:>7.2f}% 単勝 {all_win_count / all_bet_race * 100:>7.2f}%")
    print(f"総回収額: 3連単x4 {all_tierce_inquire:>8,} 3連単x1 {all_tierce_one_inquire:>8,} 3連複x4 {all_trio_inquire:>8,} 単勝 {all_win_inquire:>8,}")
    print(f"総回収率: 3連単x4 {all_tierce_inquire / all_bet * 100:>7.2f}% 3連単x1 {all_tierce_one_inquire / all_bet_race:>7.2f}% 3連複x4 {all_trio_inquire / all_bet * 100:>7.2f}% 単勝 {all_win_inquire / all_bet_race:>7.2f}%")
    print(f"総収支  : 3連単x4 {all_tierce_inquire - all_bet:>8,} 3連単x1 {all_tierce_one_inquire - all_bet_race * 100:>8,} 3連複x4 {all_trio_inquire - all_bet:>8,} 単勝 {all_win_inquire - all_bet_race * 100:>8,}")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        agreegate(sys.argv[1])
    elif len(sys.argv) == 3:
        agreegate(sys.argv[1], int(sys.argv[2]))
