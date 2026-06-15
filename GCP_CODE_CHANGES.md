# Voltstream Code Modifications for GCP & MySQL Compatibility

This document provides a detailed breakdown of every code change made to the Voltstream codebase to make it compatible with MySQL, Google Cloud Run, and Firebase Hosting.

---

## 📂 Summary of Modified Files
1. **[backend/requirements.txt](file:///c:/Users/sreek/Desktop/Voltstream/backend/requirements.txt)** (Added MySQL database drivers)
2. **[backend/app/core/config.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/core/config.py)** (Loosened config validations for database URLs)
3. **[backend/app/database.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/database.py)** (Dynamic engine connection router)
4. **[backend/app/models.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/models.py)** (String column length constraints for indexes)
5. **[backend/app/db_init.py](file:///c:/Users/sreek/Desktop/Voltstream/backend/app/db_init.py)** (SQL schema syntax correction)
6. **[frontend/.env.production](file:///c:/Users/sreek/Desktop/Voltstream/frontend/.env.production)** (Production API base URL)

---

## 🔍 Detailed File Modifications

### 1. `backend/requirements.txt`
* **Why**: SQLAlchemy requires a Python MySQL client connector (`pymysql`) to translate python commands to MySQL queries. We also installed `cryptography` because MySQL 8.x uses the `caching_sha2_password` plugin, which requires RSA encryption algorithms to authenticate securely.
* **Code Changes**:
  ```diff
   pg8000>=1.31.2
  +pymysql
  +cryptography
   google-genai==1.75.0
  ```

---

### 2. `backend/app/core/config.py`
* **Why**: The settings configuration originally validated `database_url` as a filesystem `Path`. A MySQL connection string (e.g. `mysql+pymysql://...`) is not a valid directory path and crashed Pydantic config parsing on startup. Changing the type to `str` allows connection URIs.
* **Before**:
  ```python
  database_url: Path = _path(os.getenv("DATABASE_URL", ""), BASE_DIR / "voltstream.db")
  ```
* **After**:
  ```python
  database_url: str = os.getenv("DATABASE_URL", "")
  ```

---

### 3. `backend/app/database.py`
* **Why**: The database connection engine was hardcoded to load SQLite (`sqlite:///{settings.database_url}`) and pass SQLite-specific threading arguments (`connect_args={"check_same_thread": False}`). If these arguments are passed to a MySQL dialect, SQLAlchemy throws a connection error. The updated logic dynamically routes SQLite vs MySQL based on the connection scheme.
* **Before**:
  ```python
  settings.database_url.parent.mkdir(parents=True, exist_ok=True)

  engine = create_engine(
      f"sqlite:///{settings.database_url}",
      connect_args={"check_same_thread": False},
  )
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```
* **After**:
  ```python
  from pathlib import Path
  
  db_url = settings.database_url
  connect_args = {}

  if not db_url:
      # Default to local sqlite database
      sqlite_path = BASE_DIR / "voltstream.db"
      sqlite_path.parent.mkdir(parents=True, exist_ok=True)
      db_url = f"sqlite:///{sqlite_path}"
      connect_args = {"check_same_thread": False}
  elif "://" not in db_url:
      # If it's a file name/path (like "voltstream.db"), resolve it and treat as SQLite
      sqlite_path = Path(db_url)
      if not sqlite_path.is_absolute():
          sqlite_path = BASE_DIR / sqlite_path
      sqlite_path.parent.mkdir(parents=True, exist_ok=True)
      db_url = f"sqlite:///{sqlite_path}"
      connect_args = {"check_same_thread": False}
  elif db_url.startswith("sqlite"):
      connect_args = {"check_same_thread": False}

  engine = create_engine(db_url, connect_args=connect_args)
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```

---

### 4. `backend/app/models.py`
* **Why**: SQLite allows variable-length text columns (`String`) to be indexed or serve as primary keys without defining an explicit length limit. However, MySQL restricts indexes on string columns: they must have an explicit maximum length (e.g. `String(255)`) to reserve appropriate space inside the index B-tree. Failing to specify this results in `OperationalError 1071 / 1170 (key specification without a key length)`.
* **Before (Sample)**:
  ```python
  class AnalyticsRecordModel(Base):
      __tablename__ = "analytics"
      id: Mapped[str] = mapped_column(String, primary_key=True)
      timestamp: Mapped[str] = mapped_column(String, index=True)
  ```
* **After (Sample)**:
  ```python
  class AnalyticsRecordModel(Base):
      __tablename__ = "analytics"
      id: Mapped[str] = mapped_column(String(255), primary_key=True)
      timestamp: Mapped[str] = mapped_column(String(255), index=True)
  ```
  *(Note: This modification was applied to primary keys and indexed columns across all 4 database model classes: `AnalyticsRecordModel`, `BillingRecordModel`, `DeviceModel`, and `UsageHistoryModel`).*

---

### 5. `backend/app/db_init.py`
* **Why**: The startup schema-update migrations try to add missing database columns to the `devices` table using raw SQL alter queries. In standard MySQL syntax, adding a string column requires specifying the type length (i.e. `VARCHAR(255)` instead of a raw `VARCHAR` without size), or else the engine returns a syntax error.
* **Before**:
  ```python
  if "room" not in columns:
      statements.append("ALTER TABLE devices ADD COLUMN room VARCHAR NOT NULL DEFAULT 'General'")
  ```
* **After**:
  ```python
  if "room" not in columns:
      statements.append("ALTER TABLE devices ADD COLUMN room VARCHAR(255) NOT NULL DEFAULT 'General'")
  ```

---

### 6. `frontend/.env.production`
* **Why**: During compilation, Vite bakes environment variables into the React static files. We updated this URL so the production client targets the serverless Cloud Run API rather than the local dev server.
* **Before**:
  ```text
  VITE_API_BASE_URL=https://voltstream-api-405186690499.us-central1.run.app/api/v1
  ```
* **After**:
  ```text
  VITE_API_BASE_URL=https://voltstream-backend-405186690499.us-central1.run.app/api/v1
  ```
