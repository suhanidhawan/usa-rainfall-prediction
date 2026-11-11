"""Retrain the baseline model from the included CSV."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE.parent / "data" / "usa_rain_prediction_dataset_2024_2025.csv")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Month"] = df["Date"].dt.month
df["DayOfYear"] = df["Date"].dt.dayofyear
cols = ["Location", "Temperature", "Humidity", "Wind Speed", "Precipitation",
        "Cloud Cover", "Pressure", "Month", "DayOfYear"]
X, y = df[cols], df["Rain Tomorrow"].astype(int)
cat = ["Location"]
num = [c for c in cols if c not in cat]
pre = ColumnTransformer([
    ("location", OneHotEncoder(handle_unknown="ignore"), cat),
    ("numeric", SimpleImputer(strategy="median"), num)
])
model = Pipeline([
    ("preprocess", pre),
    ("model", RandomForestClassifier(n_estimators=180, max_depth=18,
        min_samples_leaf=2, class_weight="balanced_subsample",
        random_state=42, n_jobs=-1))
])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
model.fit(Xtr, ytr)
p = model.predict(Xte)
pp = model.predict_proba(Xte)[:, 1]
metrics = {
    "accuracy": round(float(accuracy_score(yte,p)),4),
    "precision": round(float(precision_score(yte,p,zero_division=0)),4),
    "recall": round(float(recall_score(yte,p,zero_division=0)),4),
    "f1": round(float(f1_score(yte,p,zero_division=0)),4),
    "roc_auc": round(float(roc_auc_score(yte,pp)),4),
    "train_rows": len(ytr), "test_rows": len(yte)
}
joblib.dump(model, HERE / "rain_model.joblib")
(HERE / "model_metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
