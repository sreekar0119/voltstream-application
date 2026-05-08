# VoltStream

Premium full-stack smart energy monitoring platform for a solar-powered prosumer home.

## Run the backend

```bash
cd backend
python -m pip install -r requirements.txt
python generate_mock_data.py
uvicorn app.main:app --reload
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies `/api` requests to `http://127.0.0.1:8000`.

## Deploy the backend to Cloud Run

The backend is container-ready with `backend/Dockerfile`. Cloud Run sends traffic to the port in the `PORT` environment variable, and the Docker command uses that value.

```bash
cd backend
gcloud run deploy voltstream-api --source . --region us-central1 --allow-unauthenticated
```

After deployment, note the service URL printed by Google Cloud. The API docs will be available at:

```text
https://YOUR-CLOUD-RUN-SERVICE-URL/docs
```

Once the Firebase Hosting URL is known, update Cloud Run CORS:

```bash
gcloud run services update voltstream-api --region us-central1 --set-env-vars CORS_ORIGINS=https://YOUR-FIREBASE-SITE.web.app,http://localhost:5173,http://127.0.0.1:5173
```

Useful backend smoke-test URLs:

```text
https://YOUR-CLOUD-RUN-SERVICE-URL/health
https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1/dashboard/live
https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1/analytics/history
https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1/devices
https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1/billing/summary
```

## Deploy the frontend to Firebase Hosting

Build the Vite app with the Cloud Run API base URL, then deploy the generated `frontend/dist` folder with Firebase Hosting.

```bash
cd frontend
npm install
$env:VITE_API_BASE_URL="https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1"
npm run build
cd ..
firebase login
firebase use YOUR_FIREBASE_PROJECT_ID
firebase deploy --only hosting
```

Firebase Hosting serves the single-page React app from `frontend/dist`, with all browser routes rewritten to `index.html`.
