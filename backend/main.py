from pathlib import Path
from datetime import datetime
import json
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT.parent / "data" / "usa_rain_prediction_dataset_2024_2025.csv"
MODEL_PATH = ROOT / "rain_model.joblib"
MODEL = joblib.load(MODEL_PATH)
DATA = pd.read_csv(DATA_PATH)
DATA["Date"] = pd.to_datetime(DATA["Date"], errors="coerce")
LOCATIONS = sorted(DATA["Location"].dropna().unique().tolist())

app = FastAPI(
    title="USA Rainfall Prediction API",
    description="Machine-learning API for predicting whether rain is expected tomorrow.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionInput(BaseModel):
    location: str
    date: str = Field(description="Forecast date in YYYY-MM-DD format")
    temperature: float = Field(ge=-100, le=150)
    humidity: float = Field(ge=0, le=100)
    wind_speed: float = Field(ge=0, le=300)
    precipitation: float = Field(ge=0, le=1000)
    cloud_cover: float = Field(ge=0, le=100)
    pressure: float = Field(ge=800, le=1200)

@app.get("/")
def root():
    return {"message": "USA Rainfall Prediction API", "docs": "/docs", "health": "/api/health"}

@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None, "dataset_rows": int(len(DATA))}

@app.get("/api/locations")
def locations():
    return {"locations": LOCATIONS}

@app.get("/api/stats")
def stats():
    rain_rate = float(DATA["Rain Tomorrow"].mean() * 100)
    by_location = (DATA.groupby("Location")["Rain Tomorrow"].mean()
                   .mul(100).round(1).sort_values(ascending=False))
    by_month = (DATA.assign(Month=DATA["Date"].dt.month)
                .groupby("Month")["Rain Tomorrow"].mean().mul(100).round(1))
    return {
        "rows": int(len(DATA)),
        "locations_count": len(LOCATIONS),
        "date_start": DATA["Date"].min().strftime("%Y-%m-%d"),
        "date_end": DATA["Date"].max().strftime("%Y-%m-%d"),
        "rain_rate": round(rain_rate, 1),
        "dry_rate": round(100-rain_rate, 1),
        "by_location": [{"location": k, "rain_rate": float(v)} for k,v in by_location.items()],
        "by_month": [{"month": int(k), "rain_rate": float(v)} for k,v in by_month.items()],
        "metrics": json.loads((ROOT / "model_metrics.json").read_text())
    }

@app.get("/api/recent")
def recent(limit: int = 12):
    limit = max(1, min(limit, 50))
    rows = DATA.sort_values("Date", ascending=False).head(limit)
    return {"records": [
        {
            "date": r["Date"].strftime("%Y-%m-%d"),
            "location": r["Location"],
            "temperature": round(float(r["Temperature"]), 1),
            "humidity": round(float(r["Humidity"]), 1),
            "precipitation": round(float(r["Precipitation"]), 2),
            "rain_tomorrow": int(r["Rain Tomorrow"])
        } for _, r in rows.iterrows()
    ]}

@app.post("/api/predict")
def predict(payload: PredictionInput):
    if payload.location not in LOCATIONS:
        raise HTTPException(status_code=400, detail="Please select a location included in the dataset.")
    try:
        date_value = datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must use YYYY-MM-DD format.")
    row = pd.DataFrame([{
        "Location": payload.location,
        "Temperature": payload.temperature,
        "Humidity": payload.humidity,
        "Wind Speed": payload.wind_speed,
        "Precipitation": payload.precipitation,
        "Cloud Cover": payload.cloud_cover,
        "Pressure": payload.pressure,
        "Month": date_value.month,
        "DayOfYear": date_value.timetuple().tm_yday
    }])
    probability = float(MODEL.predict_proba(row)[0][1])
    prediction = int(probability >= 0.5)
    return {
        "prediction": prediction,
        "label": "Rain likely" if prediction else "Rain unlikely",
        "rain_probability": round(probability * 100, 1),
        "confidence": round(max(probability, 1-probability) * 100, 1),
        "location": payload.location,
        "date": payload.date,
        "model_note": "A statistical estimate from the supplied dataset, not an official weather forecast."
    }
