# RainScope — USA Rainfall Prediction Project

A complete local full-stack project built from the supplied `usa_rain_prediction_dataset_2024_2025.csv` (73,100 rows, 20 locations, dates 2024-01-01 to 2025-12-31).

## What's included
- **Frontend:** responsive HTML/CSS/JavaScript dashboard with overview cards, location rainfall chart, recent records table, and interactive prediction form.
- **Backend:** FastAPI REST API with health, locations, statistics, recent-records, and prediction endpoints.
- **ML model:** scikit-learn preprocessing + Random Forest classifier, already trained and saved as `backend/rain_model.joblib`.
- **Dataset:** included in `data/`.
- **Training script:** `backend/train_model.py` to retrain the model.
- **Evaluation:** holdout metrics in `backend/model_metrics.json`.

## Run in VS Code

### 1. Requirements
Install Python 3.10 or newer. Open this project folder in VS Code and open its integrated terminal.

### 2. Create and activate a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Start the API
From the project root:
```bash
uvicorn backend.main:app --reload
```
API: http://127.0.0.1:8000  
Interactive API docs: http://127.0.0.1:8000/docs

### 5. Open the frontend
Open `frontend/index.html` in your browser (or use the VS Code Live Server extension). The frontend calls the API at `http://127.0.0.1:8000`.

If your browser blocks local file requests, install the **Live Server** VS Code extension, right-click `frontend/index.html`, and choose **Open with Live Server**.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API and model status |
| GET | `/api/locations` | Dataset locations |
| GET | `/api/stats` | Dataset overview and model metrics |
| GET | `/api/recent?limit=10` | Latest CSV records |
| POST | `/api/predict` | Predict rain probability |

### Example prediction request
```json
{
  "location": "Seattle",
  "date": "2026-11-12",
  "temperature": 58,
  "humidity": 82,
  "wind_speed": 9,
  "precipitation": 1.2,
  "cloud_cover": 88,
  "pressure": 1008
}
```

## Retrain the model
```bash
python backend/train_model.py
```
This overwrites the saved model and evaluation metrics.

## Model and data notes
- Target: `Rain Tomorrow` (0 = no rain, 1 = rain).
- Features: location, temperature, humidity, wind speed, precipitation, cloud cover, pressure, month, and day of year.
- The model uses a stratified 80/20 train/test split with a fixed random seed.
- Evaluation metrics are a holdout estimate, not a guarantee of real-world forecast accuracy.
- The CSV is the source of truth for this demo. Its records end on **2025-12-31**, so a prediction for a later date is a model-based estimate from historical patterns and user-entered conditions, not a live forecast.
- This is an educational project, not an official weather service. No live weather feed is connected.

## Project structure
```text
usa-rainfall-prediction/
├── backend/
│   ├── main.py
│   ├── train_model.py
│   ├── rain_model.joblib
│   ├── model_metrics.json
│   └── requirements.txt
├── data/
│   └── usa_rain_prediction_dataset_2024_2025.csv
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── README.md
```
