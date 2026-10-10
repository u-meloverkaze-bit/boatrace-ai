"""Chronological, out-of-sample evaluation of per-ticket boat-race predictions.

Input CSV columns: date,race_id,bet_id,probability,odds,won
Optional: stake, prediction_timestamp, race_start_timestamp
Each row is a candidate bet; use odds actually available before placing a bet.
No prediction model is trained by this script: probabilities must be generated pre-race.
"""
import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_date(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def evaluate(path, min_edge=0.05, train_fraction=0.7, stake=100):
    rows = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        needed = {'date', 'race_id', 'bet_id', 'probability', 'odds', 'won'}
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError('Required columns: ' + ', '.join(sorted(needed)))
        for line, r in enumerate(reader, 2):
            try:
                p, odds, won = float(r['probability']), float(r['odds']), int(r['won'])
                assert 0 <= p <= 1 and odds > 1 and won in (0, 1)
                date = parse_date(r['date'])
                if r.get('prediction_timestamp') and r.get('race_start_timestamp'):
                    assert parse_date(r['prediction_timestamp']) < parse_date(r['race_start_timestamp']), 'post-race prediction'
                rows.append((date, r['race_id'], r['bet_id'], p, odds, won))
            except (ValueError, AssertionError, TypeError) as e:
                raise ValueError(f'Invalid row {line}: {e}') from e
    if len(rows) < 20:
        raise ValueError('At least 20 candidate tickets required; more are recommended')
    rows.sort(key=lambda x: (x[0], x[1], x[2]))
    dates = sorted({r[0].date() for r in rows})
    if len(dates) < 2:
        raise ValueError('At least 2 separate dates are required')
    cut = max(1, min(len(dates)-1, int(len(dates)*train_fraction)))
    test_dates = set(dates[cut:])
    test = [r for r in rows if r[0].date() in test_dates]
    selected = [r for r in test if r[3]*r[4] - 1 > min_edge]
    # One ticket per race to avoid inadvertently counting overlapping predictions as independent bets.
    by_race = defaultdict(list)
    for r in selected:
        by_race[(r[0].date(), r[1])].append(r)
    chosen = [max(rs, key=lambda r: (r[3]*r[4]-1, r[2])) for rs in by_race.values()]
    wagered = stake * len(chosen)
    paid = sum(stake*r[4]*r[5] for r in chosen)
    print('Validation: chronological HOLDOUT ONLY')
    print('Test dates:', min(test_dates), 'to', max(test_dates))
    print('Candidate tickets:', len(test), 'Selected bets:', len(chosen))
    print('Stake:', wagered, 'Yen; payout:', round(paid, 2), 'Yen')
    print('ROI:', f'{paid/wagered*100:.2f}%' if wagered else 'N/A (no bets)')
    print('Note: candidate probabilities must be made before races; this does not train AI.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file')
    parser.add_argument('--min-edge', type=float, default=0.05)
    args = parser.parse_args()
    evaluate(args.csv_file, args.min_edge)
