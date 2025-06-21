import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta

# Categories of budget
CATEGORIES = ["food", "transport", "entertainment", "shopping", "others"]


def build_daily_features(records):
    """
    Aggregate records into daily feature vectors.
    records: list of dicts with keys: amount, category, type, date
    Returns:
        DataFrame indexed by date with columns:
          total_spent, spent_food, spent_transport, ..., weekday, is_weekend
    """

    # Defensive: ensure each record has a 'type' key; if missing, fill as 'expense'
    clean_records = []
    for r in records:
        if not isinstance(r, dict):
            continue
        if 'type' not in r:
            r['type'] = 'expense'  # or 'unknown'
        if 'date' not in r:
            continue  # skip invalid records without date
        clean_records.append(r)

    df = pd.DataFrame(clean_records)
    if df.empty:
        return pd.DataFrame()  # empty df if no valid records

    # filter only expenses
    df = df[df['type'] == 'expense'].copy()

    # ensure 'date' is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # drop if date conversion failed

    # daily total spending
    daily_totals = df.groupby('date')['amount'].sum().rename('total_spent')

    # daily per category spending
    daily_cats = df.groupby(['date', 'category'])['amount'].sum().unstack(fill_value=0)

    # make sure all categories appear
    for cat in CATEGORIES:
        if cat not in daily_cats.columns:
            daily_cats[cat] = 0.0

    # wekday and weekend
    daily_cats = daily_cats.reset_index()
    daily_cats['weekday'] = daily_cats['date'].dt.weekday
    daily_cats['is_weekend'] = daily_cats['weekday'].apply(lambda x: 1 if x >= 5 else 0)

    daily_cats = daily_cats.set_index('date')

    # total_spent column
    daily_cats['total_spent'] = daily_totals
    daily_cats = daily_cats.fillna(0)

    # reorder columns: total_spent first, then categories, then weekday, is_weekend
    cols = ['total_spent'] + CATEGORIES + ['weekday', 'is_weekend']
    daily_cats = daily_cats[cols]

    return daily_cats


class SpendingAnomalyDetector:
    def __init__(self):
        self.model = None
        self.daily_features = None

    def train(self, daily_features):
        """
        Train Isolation Forest model on daily features DataFrame.
        Stores features internally for later use.
        """
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.model.fit(daily_features)
        self.daily_features = daily_features

    def predict(self, daily_features):
        """
        Predict anomaly scores (-1 for anomaly, 1 for normal)
        Returns:
            DataFrame with anomaly flag column
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        preds = self.model.predict(daily_features)
        results = daily_features.copy()
        results['anomaly'] = (preds == -1)
        return results

    def is_anomalous(self, new_record, all_records):
        """
        Check if a single new transaction record is anomalous.
        Approach:
          - Aggregate recent 30 days (or all if less) of records into daily features.
          - Retrain model on recent data (excluding new_record).
          - Add new_record to a new day feature vector (or existing date).
          - Predict anomaly on that single day vector.
        Returns:
          True if anomalous, False otherwise.
        """

        if not all_records or not isinstance(new_record, dict):
            return False  # no data to compare

        def to_date(r):
            try:
                return datetime.strptime(r['date'], "%Y-%m-%d").date()
            except Exception:
                return None

        today = to_date(new_record)
        if today is None:
            return False

        # include new record in recent records for last 30 days
        cutoff = today - timedelta(days=30)
        records_with_new = all_records + [new_record]
        recent_records = [r for r in records_with_new if to_date(r) is not None and to_date(r) >= cutoff]

        # Build daily features excluding new_record date
        records_excl_new_date = [r for r in recent_records if to_date(r) != today]
        features_excl_new = build_daily_features(records_excl_new_date)

        if features_excl_new.empty:
            # not enough data to train
            return False

        self.train(features_excl_new)

        # Build features for the new_record date only
        new_day_records = [r for r in recent_records if to_date(r) == today]
        features_new_day = build_daily_features(new_day_records)

        if features_new_day.empty:
            return False

        # Align columns in case categories differ
        features_new_day = features_new_day.reindex(columns=self.daily_features.columns, fill_value=0)

        preds = self.model.predict(features_new_day)
        return (preds[0] == -1)
