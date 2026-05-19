# VoltStream
full-stack smart energy monitoring platform for a solar-powered prosumer home.



## Quick Start

### Run the Backend

```bash
cd backend
python -m pip install -r requirements.txt
python generate_mock_data.py
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- API Docs: `http://127.0.0.1:8000/docs`

### Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: `http://localhost:5173` or `http://127.0.0.1:5173`
- The frontend proxies `/api` requests to `http://127.0.0.1:8000`

## Deploy to Cloud

### Deploy Backend to Google Cloud Run

```bash
cd backend
gcloud run deploy voltstream-api --source . --region us-central1 --allow-unauthenticated
```

### Deploy Frontend to Firebase Hosting

```bash
cd frontend
$env:VITE_API_BASE_URL="https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1"
npm run build
cd ..
firebase login
firebase use YOUR_FIREBASE_PROJECT_ID
firebase deploy --only hosting
```



