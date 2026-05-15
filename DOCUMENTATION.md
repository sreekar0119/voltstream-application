# VoltStream - Smart Energy Monitoring Platform
## Complete Project Documentation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Use Case](#use-case)
3. [Project Architecture](#project-architecture)
4. [Project Structure](#project-structure)
5. [Backend Files Explained](#backend-files-explained)
6. [Frontend Files Explained](#frontend-files-explained)
7. [Cloud Deployment Architecture](#cloud-deployment-architecture)
8. [Local Development Setup](#local-development-setup)
9. [Cloud Deployment Guide](#cloud-deployment-guide)
10. [API Endpoints Reference](#api-endpoints-reference)
11. [Commands Quick Reference](#commands-quick-reference)
12. [Technology Stack](#technology-stack)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

**VoltStream** is a premium full-stack smart energy monitoring platform designed for solar-powered prosumer homes. It provides real-time visibility into energy consumption, generation, costs, and device management through an intuitive web-based dashboard.

---

## Use Case

VoltStream is built for prosumers (producer-consumers) who own solar panels and want to:
- **Monitor Energy in Real-Time**: Track live energy consumption and solar generation
- **Analyze Usage Patterns**: View historical analytics and identify consumption trends
- **Manage Devices**: Control and monitor smart energy devices on the network
- **Track Billing**: Understand energy costs and billing cycles
- **Optimize Consumption**: Make data-driven decisions to reduce energy costs

---

## Project Architecture

VoltStream follows a **client-server architecture**:
- **Frontend**: Modern React SPA (Single Page Application) built with Vite
- **Backend**: RESTful API built with FastAPI (Python)
- **Cloud Infrastructure**: Deployed on Google Cloud (Cloud Run for backend, Firebase Hosting for frontend)

```
┌─────────────────────────────────────────┐
│   Frontend (React/Vite)                 │
│   Firebase Hosting                      │
└─────────────────────────────────────────┘
              ↓ (HTTP/REST)
┌─────────────────────────────────────────┐
│   Backend API (FastAPI)                 │
│   Google Cloud Run                      │
└─────────────────────────────────────────┘
```

---

## Project Structure

### Root Directory
```
VoltStream/
├── README.md                 # Quick start guide
├── DOCUMENTATION.md          # This file - detailed documentation
├── backend/                  # Python FastAPI Backend
└── frontend/                 # React/Vite Frontend
```

### Backend Structure (`backend/`)
```
backend/
├── Dockerfile                # Docker container definition for Cloud Run
├── requirements.txt          # Python dependencies
├── env-vars.yaml             # Environment variables configuration
├── generate_mock_data.py     # Script to generate mock data for testing
├── mock_data/                # Mock JSON data files
│   ├── analytics.json        # Sample analytics data
│   ├── billing.json          # Sample billing data
│   └── devices.json          # Sample device data
└── app/                      # Main application directory
    ├── __init__.py           # Package initialization
    ├── main.py               # FastAPI application entry point
    ├── core/                 # Core configuration
    │   ├── __init__.py
    │   └── config.py         # Settings and environment configuration
    ├── routers/              # API endpoint definitions
    │   ├── __init__.py
    │   ├── analytics.py      # Analytics API endpoints
    │   ├── billing.py        # Billing API endpoints
    │   ├── dashboard.py      # Dashboard API endpoints
    │   └── devices.py        # Device management API endpoints
    ├── schemas/              # Pydantic data models for request/response
    │   ├── __init__.py
    │   ├── analytics.py      # Analytics data schemas
    │   ├── billing.py        # Billing data schemas
    │   ├── dashboard.py      # Dashboard data schemas
    │   └── devices.py        # Device data schemas
    ├── services/             # Business logic layer
    │   ├── __init__.py
    │   ├── analytics_service.py    # Analytics business logic
    │   ├── billing_service.py      # Billing calculations
    │   ├── dashboard_service.py    # Dashboard data aggregation
    │   └── device_service.py       # Device management logic
    └── utils/                # Utility functions
        ├── __init__.py
        └── data_loader.py    # Helper functions for data loading
```

### Frontend Structure (`frontend/`)
```
frontend/
├── package.json              # Node.js dependencies and scripts
├── vite.config.js            # Vite build configuration
├── firebase.json             # Firebase Hosting configuration
├── eslint.config.js          # ESLint rules for code quality
├── index.html                # HTML entry point
├── src/                      # React application source code
│   ├── main.jsx              # React entry point (renders App)
│   ├── styles.css            # Global CSS styles
│   ├── animations/           # Framer Motion animation definitions
│   │   └── variants.js       # Reusable animation variants
│   ├── charts/               # Recharts chart components
│   │   ├── BillingChart.jsx  # Billing costs visualization
│   │   ├── CostChart.jsx     # Cost analysis chart
│   │   ├── DeviceCategoryChart.jsx  # Device breakdown by category
│   │   ├── EnergyAreaChart.jsx      # Energy consumption area chart
│   │   └── GridDrawChart.jsx        # Grid power draw chart
│   ├── components/           # Reusable UI components
│   │   ├── AlertBanner.jsx   # Alert notification display
│   │   ├── ChartCard.jsx     # Wrapper for chart visualizations
│   │   ├── DeviceCard.jsx    # Individual device display card
│   │   ├── EmptyState.jsx    # Empty state placeholder
│   │   ├── EnergyGauge.jsx   # Circular energy gauge visualization
│   │   ├── GlassPanel.jsx    # Glassmorphic panel container
│   │   ├── LoadingState.jsx  # Loading spinner and skeleton
│   │   ├── MetricCard.jsx    # Key metric display card
│   │   ├── ProgressBar.jsx   # Progress bar indicator
│   │   ├── Sidebar.jsx       # Navigation sidebar
│   │   ├── StatusPill.jsx    # Status badge component
│   │   ├── Toggle.jsx        # Toggle switch component
│   │   └── Topbar.jsx        # Top navigation bar
│   ├── hooks/                # Custom React hooks
│   │   └── useApi.js         # API data fetching hook
│   ├── layouts/              # Page layout components
│   │   └── AppShell.jsx      # Main application shell wrapper
│   ├── pages/                # Full-page components (routes)
│   │   ├── LiveDashboard.jsx # Real-time energy monitoring
│   │   ├── SmartControl.jsx  # Device control interface
│   │   ├── UsageHistory.jsx  # Historical usage analytics
│   │   ├── Invoices.jsx      # Billing invoice viewer
│   │   └── NotFound.jsx      # 404 error page
│   ├── routes/               # Routing configuration
│   │   └── router.jsx        # React Router configuration
│   ├── services/             # API client and external services
│   │   └── api.js            # Axios API client setup
│   └── utils/                # Utility functions
│       └── format.js         # Data formatting utilities
```

---

## Backend Files Explained

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application initialization with CORS middleware and router registration |
| `config.py` | Pydantic settings for app configuration, API version, CORS origins, and environment variables |

### API Routers (Endpoints)

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `analytics.py` | `/api/v1/analytics/*` | Historical energy analytics, trends, and reports |
| `billing.py` | `/api/v1/billing/*` | Billing information, costs, and invoice data |
| `dashboard.py` | `/api/v1/dashboard/*` | Live dashboard data (real-time metrics and status) |
| `devices.py` | `/api/v1/devices/*` | Smart device management (list, control, monitor) |

### Services (Business Logic)

| Service | Responsibility |
|---------|-----------------|
| `analytics_service.py` | Processes and aggregates historical energy data |
| `billing_service.py` | Calculates costs, rates, and billing summaries |
| `dashboard_service.py` | Aggregates real-time metrics for dashboard display |
| `device_service.py` | Manages device inventory, status, and control logic |

### Data Schemas (Pydantic Models)

Located in `schemas/` directory, these define the structure of API requests and responses:
- `analytics.py` - Analytics data models
- `billing.py` - Billing data models
- `dashboard.py` - Dashboard data models
- `devices.py` - Device data models

### Utilities & Data

| File | Purpose |
|------|---------|
| `data_loader.py` | Loads mock data from JSON files for testing |
| `generate_mock_data.py` | Generates sample data for development/testing |
| `requirements.txt` | Python package dependencies |
| `Dockerfile` | Container image definition for Cloud Run deployment |

---

## Frontend Files Explained

### Page Components (Routes)

| Page | Purpose |
|------|---------|
| `LiveDashboard.jsx` | Real-time energy monitoring and status overview |
| `SmartControl.jsx` | Interface to control and manage connected devices |
| `UsageHistory.jsx` | Historical energy usage analytics and visualizations |
| `Invoices.jsx` | View and manage billing invoices |
| `NotFound.jsx` | 404 error page for invalid routes |

### Reusable Components

| Component | Purpose |
|-----------|---------|
| `MetricCard.jsx` | Display key metrics (kWh, cost, efficiency, etc.) |
| `ChartCard.jsx` | Container wrapper for chart visualizations |
| `DeviceCard.jsx` | Display individual smart device status and controls |
| `EnergyGauge.jsx` | Circular gauge showing energy levels |
| `ProgressBar.jsx` | Visual indicator for percentages and progress |
| `GlassPanel.jsx` | Glassmorphic UI panel for modern aesthetics |
| `Sidebar.jsx` | Navigation menu for page routing |
| `Topbar.jsx` | Header with branding and user controls |
| `AlertBanner.jsx` | Display alerts and notifications |
| `StatusPill.jsx` | Badge showing online/offline status |
| `Toggle.jsx` | Switch component for boolean options |
| `LoadingState.jsx` | Skeleton loading states |
| `EmptyState.jsx` | Placeholder for empty data states |

### Chart Components

| Chart | Purpose |
|-------|---------|
| `EnergyAreaChart.jsx` | Area chart showing energy consumption over time |
| `BillingChart.jsx` | Visualize billing costs |
| `CostChart.jsx` | Cost analysis and breakdown |
| `DeviceCategoryChart.jsx` | Energy usage by device category |
| `GridDrawChart.jsx` | Power draw from/to grid visualization |

### Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Node dependencies (React, Vite, TailwindCSS, Recharts, etc.) |
| `vite.config.js` | Vite bundler configuration |
| `firebase.json` | Firebase Hosting deployment configuration |
| `eslint.config.js` | Code quality linting rules |

### Other

| File | Purpose |
|------|---------|
| `router.jsx` | React Router configuration defining all routes |
| `useApi.js` | Custom hook for API calls with loading/error states |
| `api.js` | Axios client configured for backend base URL |
| `format.js` | Utility functions for formatting numbers, dates, etc. |
| `variants.js` | Framer Motion animation definitions for consistent motion |

---

## Cloud Deployment Architecture

### Backend Deployment (Google Cloud Run)

**What is Cloud Run?**
Cloud Run is a serverless compute platform that automatically scales your containerized backend. You only pay for the compute time your API uses.

**Deployment Process:**
1. Docker container is built from `backend/Dockerfile`
2. Image is pushed to Google Container Registry
3. Cloud Run deploys the container with automatic scaling
4. API is accessible via public HTTPS URL

**Why Docker?**
- Ensures consistent environment between local and cloud
- Easy reproducibility across teams
- Cloud Run natively supports Docker containers

### Frontend Deployment (Firebase Hosting)

**What is Firebase Hosting?**
Firebase Hosting provides secure, fast, and reliable hosting for your static web app with automatic HTTPS and global CDN.

**Deployment Process:**
1. Frontend is built to static files (HTML, CSS, JS) using `npm run build`
2. Generated `frontend/dist` folder is deployed to Firebase Hosting
3. Firebase configures routing to serve `index.html` for all routes (SPA support)
4. Content is globally distributed via CDN

**Why Firebase?**
- Zero-config HTTPS and global CDN
- Easy GitHub integration for continuous deployment
- Integrated with Google Cloud ecosystem
- Cost-effective for static content

---

## Local Development Setup

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a Python virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Mac/Linux

# Install dependencies
python -m pip install -r requirements.txt

# Generate mock data for testing
python generate_mock_data.py

# Start the development server
uvicorn app.main:app --reload
```

**Backend will be available at:**
- API: `http://127.0.0.1:8000`
- Interactive API docs: `http://127.0.0.1:8000/docs`
- ReDoc documentation: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:**
- App: `http://localhost:5173` or `http://127.0.0.1:5173`
- The frontend automatically proxies `/api` requests to the backend at `http://127.0.0.1:8000`

---

## Cloud Deployment Guide

### Step 1: Deploy Backend to Google Cloud Run

```bash
# Ensure you're in the backend directory
cd backend

# Deploy to Cloud Run
gcloud run deploy voltstream-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# Example output:
# Service URL: https://voltstream-api-xxxxx.run.app
```

**Note:** Save the Cloud Run service URL (e.g., `https://voltstream-api-xxxxx.run.app`) - you'll need it for the frontend.

**Verify Backend Deployment:**
```bash
# Check health endpoint
curl https://YOUR-CLOUD-RUN-SERVICE-URL/health

# View API documentation
# Open in browser: https://YOUR-CLOUD-RUN-SERVICE-URL/docs
```

### Step 2: Configure Cloud Run CORS

Once you know the Firebase Hosting URL, update CORS settings:

```bash
gcloud run services update voltstream-api \
  --region us-central1 \
  --set-env-vars CORS_ORIGINS=https://YOUR-FIREBASE-SITE.web.app,http://localhost:5173,http://127.0.0.1:5173
```

### Step 3: Build Frontend with Cloud Backend URL

```bash
cd frontend

# Set the Cloud Run API URL as environment variable
# On Windows PowerShell:
$env:VITE_API_BASE_URL="https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1"

# On Mac/Linux:
export VITE_API_BASE_URL="https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1"

# Build for production
npm run build

# This creates optimized static files in frontend/dist
```

### Step 4: Deploy Frontend to Firebase Hosting

```bash
# Authenticate with Firebase (one-time setup)
firebase login

# Set your Firebase project
firebase use YOUR_FIREBASE_PROJECT_ID

# Deploy to Firebase Hosting
firebase deploy --only hosting

# Example output:
# Hosting URL: https://your-project-id.web.app
```

---

## API Endpoints Reference

### Dashboard Endpoints
```
GET  /api/v1/dashboard/live          - Live dashboard metrics
```

### Analytics Endpoints
```
GET  /api/v1/analytics/history       - Historical analytics data
GET  /api/v1/analytics/trends        - Energy trends
GET  /api/v1/analytics/summary       - Analytics summary
```

### Device Endpoints
```
GET  /api/v1/devices                 - List all devices
GET  /api/v1/devices/{device_id}     - Get device details
POST /api/v1/devices/{device_id}/control - Control device
```

### Billing Endpoints
```
GET  /api/v1/billing/summary         - Billing summary
GET  /api/v1/billing/invoices        - List invoices
GET  /api/v1/billing/costs           - Cost details
```

---

## Commands Quick Reference

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python generate_mock_data.py
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### Production Build
```bash
# Backend
cd backend
gcloud run deploy voltstream-api --source . --region us-central1 --allow-unauthenticated

# Frontend
cd frontend
$env:VITE_API_BASE_URL="https://YOUR-CLOUD-RUN-SERVICE-URL/api/v1"
npm run build
firebase deploy --only hosting
```

### Useful Cloud Commands
```bash
# View Cloud Run logs
gcloud run logs read voltstream-api --region us-central1 --limit 50

# Update environment variables
gcloud run services update voltstream-api --region us-central1 --set-env-vars KEY=VALUE

# View current CORS settings
gcloud run services describe voltstream-api --region us-central1
```

---

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **Uvicorn**: ASGI web server
- **Pydantic**: Data validation using Python type hints
- **Docker**: Containerization
- **Python 3.10+**

### Frontend
- **React 18**: UI library
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **TailwindCSS**: Utility-first CSS framework
- **Recharts**: React charting library
- **Framer Motion**: Animation library
- **Lucide React**: Icon library

### Cloud Infrastructure
- **Google Cloud Run**: Serverless backend hosting
- **Firebase Hosting**: Static frontend hosting
- **Google Cloud Container Registry**: Docker image storage

---

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port with `uvicorn app.main:app --port 8001`
- **Module not found**: Ensure Python virtual environment is activated
- **CORS errors**: Update `CORS_ORIGINS` environment variable

### Frontend Issues
- **API not responding**: Verify backend is running and check `VITE_API_BASE_URL`
- **Build fails**: Run `npm install` to ensure all dependencies are installed
- **Port conflict**: Vite will auto-select next available port

### Cloud Deployment Issues
- **Cloud Run deployment fails**: Check Docker build logs with `gcloud builds log`
- **CORS errors on cloud**: Ensure CORS environment variable is set correctly
- **Firebase deployment fails**: Verify project ID and authentication status

---

## Support & Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Firebase Hosting Docs](https://firebase.google.com/docs/hosting)
- [Vite Documentation](https://vitejs.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
