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

mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"

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





# 🛠 Ensure the database exists
echo "🧙 Checking if database '$DB_NAME' exists..."

DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "📗 Database '$DB_NAME' not found. Creating it..."
    sudo -u postgres createdb "$DB_NAME"
else
    echo "💣 Dropping database '$DB_NAME' if it exists..."
    sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
    sudo -u postgres dropdb --if-exists "$DB_NAME"
    
    echo "📗 Creating fresh database '$DB_NAME' owned by postgres..."
    sudo -u postgres createdb "$DB_NAME"
fi



echo "📐 Ensuring 'edfi' schema exists and 'xenda' can use it..."
sudo -u postgres psql -d "$DB_NAME" <<EOF
CREATE SCHEMA IF NOT EXISTS edfi AUTHORIZATION postgres;
GRANT USAGE ON SCHEMA edfi TO xenda;
GRANT CREATE ON SCHEMA edfi TO xenda;
CREATE SCHEMA IF NOT EXISTS edfi AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS auth AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS interop AUTHORIZATION postgres;
CREATE SCHEMA IF NOT EXISTS util AUTHORIZATION postgres;
GRANT USAGE ON SCHEMA edfi TO xenda;
GRANT CREATE ON SCHEMA edfi TO xenda;
ALTER DEFAULT PRIVILEGES IN SCHEMA edfi GRANT ALL ON TABLES TO xenda;
EOF


if [ -f "$EXTRACTED_SQL" ]; then
  echo "💾 Restoring SQL into PostgreSQL ($DB_NAME)..."
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$EXTRACTED_SQL"
  echo "🎉 Ed-Fi Glendale database restored successfully into $DB_NAME!"
else
  echo "❌ SQL file not found. Did the 7z extract fail?"
  exit 1
fi


echo "🧼 Reassigning object ownership to user '$DB_USER'..."
SQL_FILE="$(pwd)/$BACKUP_DIR/$EXTRACTED_SQL"
sudo -u postgres psql -d "$DB_NAME" -f "$SQL_FILE"
