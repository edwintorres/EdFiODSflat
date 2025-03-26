# 🚀 EdFiODSflat Setup Guide

Welcome to the **EdFiODSflat** project! This guide will help you get your environment ready for smooth PySpark + Jupyter Notebook development in **WSL2**, **Docker**, and **VS Code**.

---

## 📚 Table of Contents

- [🚀 EdFiODSflat Setup Guide](#-edfiodsflat-setup-guide)
- [🧰 Prerequisites (Install These First)](#-prerequisites-install-these-first)
- [🛠️ Project Setup Steps](#️-project-setup-steps)
- [🧪 Verify Your Setup](#-verify-your-setup)
- [💻 Open Project in VS Code Dev Container (Jupyter Inside VS Code)](#-open-project-in-vs-code-dev-container-jupyter-inside-vs-code)
- [🧯 Trouble with WSL dropping you into root@...?](#-trouble-with-wsl-dropping-you-into-root)
- [🧼 Cleanup & Rebuild](#-cleanup--rebuild)
- [🔁 Full Docker Reset (Cleanup)](#-full-docker-reset-cleanup)
---


## 🧰 Prerequisites (Install These First)

Before running anything, make sure you've got these installed and working:

### ✅ On Windows:
- [x] **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**  
  ⮕ Be sure to enable **WSL 2 integration** in the Docker settings.

- [x] **[Windows Subsystem for Linux 2 (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install)**  
  ⮕ Use **Ubuntu 22.04** as your distro.

- [x] **[Visual Studio Code](https://code.visualstudio.com/)**  
  ⮕ With these extensions:
    - **Remote - WSL**
    - **Remote - Containers**
    - **Jupyter**
    - **Python**

---

## 🛠️ Project Setup Steps

1. **Clone this repo inside your WSL Ubuntu directory:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/EdFiODSflat.git
   cd EdFiODSflat
   ```

2. **Run the installer:**
   ```bash
   ./setup/install_wsl_tools.sh
   ```

   This will install:
   - Java 16 via SDKMAN
   - Apache Spark 3.5.0
   - PySpark + Jupyter + Databricks CLI
   - Docker + Docker Compose
   - Setup Jupyter password (`edfi` by default)
   - Create a test PySpark script

3. **Apply Docker group change without rebooting:**
   ```bash
   newgrp docker
   ```

---

## 🧪 Verify Your Setup

To test CSV reading with Spark:
```bash
python3 ./scripts/test_pyspark_read.py
```

To run the test inside the Docker container:
```
docker compose run spark-jupyter python /workspace/scripts/test_pyspark_read.py
```

To launch Jupyter in the browser manually:
```bash
jupyter lab --no-browser --ip=127.0.0.1 --port=8888
```

Password: `edfi`

---

## 💻 Open Project in VS Code Dev Container (Jupyter Inside VS Code)

1. Launch **VS Code** from inside WSL:
   ```bash
   code .
   ```

2. When prompted, choose:
   ```
   Reopen in Container
   ```

   Or use the Command Palette:
   ```
   > Dev Containers: Reopen in Container
   ```

3. The container will spin up using:
   - `docker-compose.yml`
   - `Dockerfile.spark`
   - `/workspace` folder mapped to your local repo

4. Once it finishes building, open the notebook:
   ```
   notebooks/edfi_spark_query.ipynb
   ```

   Jupyter will now run **inside the container**, with access to Spark and your data.

---

## 🐘 Load the Ed-Fi Glendale Sample Database (PostgreSQL)

Want a fully-loaded **Ed-Fi ODS** to play with? Just run one command and *boom* — the **Glendale v5.3** sample data will be restored into your local PostgreSQL. 🎉

### 📦 Step 1: Run the installer

```bash
./setup/install_edfi.sh
```

This script will:

- 📥 Download the **Glendale v5.3** `.7z` PostgreSQL dump
- 🗜️ Extract the `.sql` file
- 💣 Drop and recreate the `edfi_db` database
- 🧱 Create required schemas (`edfi`, `auth`, `interop`, `util`)
- 🔐 Create the `pgcrypto` extension
- 🛡 Grant schema access to the `xenda` user
- 💾 Restore all schema and sample data into `edfi_db` using `postgres`

Your local DB config will be:

| Setting     | Value        |
|-------------|--------------|
| Host        | `localhost`  |
| Port        | `5432`       |
| Database    | `edfi_db`    |
| Username    | `xenda`      |
| Password    | `Xenda123!`  |

> **Note:** If the DB already exists, it will be dropped and rebuilt from scratch. Don't store anything personal in there 💋

---

### 🔍 Step 2: Query the database

#### 🐚 From CLI:

```bash
PGPASSWORD='Xenda123!' psql -U xenda -d edfi_db -h localhost -c "SELECT * FROM edfi.student LIMIT 5;"
```

#### 🧪 From Jupyter / Python:

```python
import psycopg2

conn = psycopg2.connect(
    dbname="edfi_db",
    user="xenda",
    password="Xenda123!",
    host="localhost",
    port=5432
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM edfi.student LIMIT 5;")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()
```

---



---

## 🧯 Trouble with WSL dropping you into root@...?

Read this fix to avoid tool issues (Jupyter, SDKMAN, etc):

[/docs/fix-wsl-root-readme.md](/docs/fix-wsl-root-readme.md)


---

## 🧼 Cleanup & Rebuild

To stop and clean Docker:
```bash
docker compose down
```

To rebuild from scratch:
```bash
docker compose up --build
```

## 🔁 Full Docker Reset (Cleanup)
If things get weird, containers won’t stop, or you renamed services and Docker’s confused… run this:
```
docker compose down --volumes --remove-orphans
```
This will:
* 🗑️ Stop all containers
* 💣 Delete all volumes (including cached data)
* 👻 Remove orphan containers (leftover ghosts from old runs)

💡 Use this when switching container names, debugging, or doing a full reset.

---

Happy coding! 💥


---
sudo chown -R etorr:etorr /home/etorr/repos/EdFiODSflat





