import csv
import argparse

def backtest(filename, min_edge=0.05):
    bets = 0
    total_stake = 0
    total_return = 0

    with open(filename, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            probability = float(row["probability"])
            odds = float(row["odds"])
            won = int(row["won"])

            if probability * odds - 1 <= min_edge:
                continue

            bets += 1
            total_stake += 100
            if won == 1:
                total_return += 100 * odds

    print("購入件数:", bets)
    print("投資金額:", total_stake, "円")
    print("払戻金額:", total_return, "円")
    if total_stake:
        print("回収率:", round(total_return / total_stake * 100, 2), "%")
    else:
        print("対象レースなし")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    args = parser.parse_args()
    backtest(args.csv_file)
