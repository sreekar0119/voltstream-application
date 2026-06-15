# Voltstream GCP Production Deployment Summary & Troubleshooting Log

This document contains a complete step-by-step history of how the Voltstream application was configured, deployed, and debugged for production on Google Cloud Platform (GCP).

---

## 🏗️ Target Architecture
- **Frontend**: React/Vite static site hosted on **Firebase Hosting**.
- **Backend API**: FastAPI containerized server running on **Google Cloud Run**.
- **Database**: Managed **Google Cloud SQL (MySQL)** instance.
- **Vector Database**: Pre-populated **Chroma DB** packaged directly inside the backend Docker container (read-only mode).
- **LLM Integration**: **Google Cloud Vertex AI** (Gemini 2.5 Flash).

---

## 🛠️ Step-by-Step Deployment History & Issues Resolved

### Phase 1: Code Updates for MySQL Compatibility
To transition from SQLite (local development) to MySQL (GCP Cloud SQL), we made the following code modifications:

1. **Backend Dependencies**: Added `pymysql` and `cryptography` to [backend/requirements.txt](file:///c:/Users/sreek/Desktop/Voltstream/backend/requirements.txt) to allow SQLAlchemy to connect to a MySQL database.
2. **Pydantic Configs**: Changed the `database_url` type from `Path` to `str` in [backend/app/core/config.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/core/config.py) to support database connection strings.
3. **Database Engine**: Refactored [backend/app/database.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/database.py) to dynamically construct the SQLAlchemy engine based on the connection scheme (retaining SQLite configuration for local testing, but loading MySQL configuration dynamically for production).
4. **Table Constraints**: Updated [backend/app/models.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/models.py) to declare explicit length parameters (e.g. `String(255)`) on all key and indexed columns. MySQL requires explicit string lengths for indexes.
5. **Schema Alterations**: Updated [backend/app/db_init.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/db_init.py) to specify `VARCHAR(255)` in its SQLite/MySQL schema alteration statements.

---

### Phase 2: Local Verification & Docker Setup
Before uploading code to the cloud, we verified the container startup behavior.

#### ❌ Error 1: Local SQLite startup failed
* **Error message**:
  `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string 'voltstream.db'`
* **Cause**: In the local `.env` file, the `DATABASE_URL` was configured as a relative file name (`voltstream.db`). Without the `sqlite:///` prefix, SQLAlchemy tried to parse it as an external server name.
* **Resolution**: Updated `database.py` with path-checking logic: if the database URL lacks a protocol scheme (like `://`), the code automatically treats it as a relative SQLite path, resolves it, and prepends the correct `sqlite:///` connection string.

#### ❌ Error 2: Local Docker daemon connection failed
* **Error message**:
  `ERROR: failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine...`
* **Cause**: The command `docker build` was run while the Docker Desktop application was shut down on the local Windows machine.
* **Resolution**: Started the **Docker Desktop** application and waited for the engine status to turn green.
* **Verification**: Ran `docker build -t voltstream-backend:local .` and started it locally using `docker run -p 8080:8080 voltstream-backend:local`. Confirmed `/health` and `/docs` endpoints responded with `200 OK`.

---

### Phase 3: GCP Infrastructure Creation
In the Google Cloud Console, we enabled APIs and provisioned resource groups:

1. **APIs Enabled**: Cloud Run API, Cloud SQL Admin API, Artifact Registry API, and Vertex AI API.
2. **Cloud SQL (MySQL) Instance**:
   - Instance ID: `voltstream-db`
   - Version: MySQL 8.4 (Enterprise Plus trial tier)
   - Database created: `voltstream`
   - User account created: `voltstream-db` (Host: `% (any host)`)
3. **Artifact Registry Repository**:
   - Repository ID: `voltstream-repo`
   - Format: Docker
   - Region: `us-central1`

---

### Phase 4: Container Upload & Cloud Run Troubleshooting

We configured Docker authentication, built the production image, and uploaded it to the registry:
```powershell
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -t us-central1-docker.pkg.dev/project-742c5695-e214-4aff-900/voltstream-repo/backend:latest .
docker push us-central1-docker.pkg.dev/project-742c5695-e214-4aff-900/voltstream-repo/backend:latest
```

#### ❌ Error 3: Database access denied (User/DB missing)
* **Error message**:
  `sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied for user 'voltstream-user'...")`
* **Cause**: The database connection parameters inside the container deployment configuration pointed to a database `voltstream` and user `voltstream-user` which had not yet been created in the Cloud SQL console.
* **Resolution**: Created the database `voltstream` in the Cloud SQL "Databases" tab, and added the user account `voltstream-db` in the "Users" tab.

#### ❌ Error 4: Database connection credentials parse error
* **Error message**:
  `sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied for user 'voltstream-db'...")`
* **Cause**: The database password `Sreekar@2004` contained the special character `@`. In database connection strings, `@` is the separator token between passwords and hosts. The parser split the string at the `@` symbol, truncating the password to `Sreekar`.
* **Resolution**: URL-encoded the `@` symbol to `%40` in the connection string:
  `mysql+pymysql://voltstream-db:Sreekar%402004@/voltstream?unix_socket=/cloudsql/...`

#### ❌ Error 5: Cloud Run Container OOM (Out Of Memory) Crash
* **Error message**:
  `Memory limit of 512 MiB exceeded with 602 MiB used. Container failed to start and listen on port.`
* **Cause**: To perform search operations on the pre-loaded PDF vector database, the container loads the `sentence-transformers` library and the `all-MiniLM-L6-v2` embedding model. This requires about 600-700 MiB of memory, which exceeded Cloud Run's default memory allocation of 512 MiB.
* **Resolution**: Increased the memory allocation of the Cloud Run instance to **2 GiB** by running:
  ```powershell
  gcloud run services update voltstream-backend --memory=2Gi --region=us-central1
  ```
  This immediately resolved the OOM crashes, allowing the container to boot, initialize, and process requests.

---

### Phase 5: Frontend Build & Deployment

#### ❌ Error 6: Dashboard showing "⚠️ Not Found"
* **Cause**: 
  1. The API base URL in [frontend/.env.production](file:///c:/Users/sreek/Desktop/Voltstream/frontend/.env.production) was configured with the wrong service prefix (`voltstream-api` instead of `voltstream-backend`).
  2. The `/api/v1` suffix was missing from the endpoint base URL.
  3. The frontend was not rebuilt after updating the environment variables (Vite embeds env variables during compilation/build time, not runtime).
* **Resolution**: 
  1. Updated `frontend/.env.production` to point to the correct URL:
     `VITE_API_BASE_URL=https://voltstream-backend-405186690499.us-central1.run.app/api/v1`
  2. Ran `npm run build` to compile the new endpoint path.
  3. Ran `npx firebase-tools deploy` to publish the updated bundle.

---

## 🎉 Live Results
Both components are live and communicating successfully:
- **Frontend App**: [https://voltstream-app-493ba.web.app](https://voltstream-app-493ba.web.app)
- **Backend API URL**: [https://voltstream-backend-405186690499.us-central1.run.app/health](https://voltstream-backend-405186690499.us-central1.run.app/health)
