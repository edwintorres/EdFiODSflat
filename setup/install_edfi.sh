#!/usr/bin/env bash
set -e

# 🎯 Config
BACKUP_URL="https://odsassets.blob.core.windows.net/public/Glendale/EdFi_Ods_Glendale_v53_20220120_PG11.7z"
BACKUP_DIR="sql/edfi_glendale"
BACKUP_NAME="EdFi_Ods_Glendale_v53_20220120_PG11.7z"
EXTRACTED_SQL="EdFi_Ods_Glendale_v53_PG11.sql"
DB_NAME="edfi_db"
DB_USER="xenda"
DB_PASSWORD="Xenda123!"
DB_HOST="localhost"
DB_PORT="5432"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FULL_BACKUP_DIR="$PROJECT_ROOT/$BACKUP_DIR"
SQL_FILE="$FULL_BACKUP_DIR/$EXTRACTED_SQL"

mkdir -p "$FULL_BACKUP_DIR"
cd "$FULL_BACKUP_DIR"

# 🧲 Download backup
if [ ! -f "$BACKUP_NAME" ]; then
  echo "📥 Downloading Glendale backup..."
  curl -LO "$BACKUP_URL"
else
  echo "✅ Backup already downloaded."
fi

# 🗜 Unzip using p7zip
if ! command -v 7z &> /dev/null; then
  echo "🧰 Installing p7zip-full..."
  sudo apt-get install -y p7zip-full
fi

if [ ! -f "$EXTRACTED_SQL" ]; then
  echo "📂 Extracting .7z file..."
  7z e "$BACKUP_NAME"
else
  echo "✅ SQL file already extracted."
fi

# ⚙️ Ensure postgres can access the folder
chmod +x "$PROJECT_ROOT" "$PROJECT_ROOT/sql" "$FULL_BACKUP_DIR"

# 💣 Drop & recreate database
echo "🧙 Checking if database '$DB_NAME' exists..."
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
sudo -u postgres dropdb --if-exists "$DB_NAME"
echo "📗 Creating fresh database '$DB_NAME' owned by postgres..."
sudo -u postgres createdb "$DB_NAME"

# 🧱 Ensure schemas + access
echo "📐 Ensuring schemas and privileges..."
sudo -u postgres psql -d "$DB_NAME" <<EOF
CREATE SCHEMA IF NOT EXISTS edfi AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS interop AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS util AUTHORIZATION postgres;
GRANT USAGE ON SCHEMA edfi TO xenda;
GRANT CREATE ON SCHEMA edfi TO xenda;
ALTER DEFAULT PRIVILEGES IN SCHEMA edfi GRANT ALL ON TABLES TO xenda;
EOF

# 🔌 Enable extensions (like pgcrypto)
echo "🔌 Enabling required extensions..."
sudo -u postgres psql -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS o;"

# 💾 Restore SQL dump
echo "💾 Restoring SQL into PostgreSQL ($DB_NAME)..."
sudo -u postgres psql -d "$DB_NAME" -f "$SQL_FILE"

echo "✅ Ed-Fi Glendale PostgreSQL DB restored successfully!"

