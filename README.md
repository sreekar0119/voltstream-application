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
