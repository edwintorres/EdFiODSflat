#!/usr/bin/env bash
set -e  # 💥 Stop on any error

# 🏁 Optional: pass --force to reinstall Spark
FORCE=false
if [[ "$1" == "--force" ]]; then
  FORCE=true
fi

echo "🔄 Updating package lists..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "🐍 Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip

echo "📦 Installing dependencies: unzip, curl, zip..."
sudo apt-get install -y unzip curl zip

echo "📡 Checking for SDKMAN..."
if [ -d "$HOME/.sdkman" ]; then
  echo "✅ SDKMAN is already installed."
else
  echo "📥 Installing SDKMAN..."
  curl -s "https://get.sdkman.io" | bash
fi

# 🧠 Load SDKMAN into the current shell
# shellcheck source=/dev/null
source "$HOME/.sdkman/bin/sdkman-init.sh"

echo "☕ Installing Java 16 via SDKMAN..."
sdk install java 16.0.2-open

# 🔥 Spark setup
SPARK_VERSION=3.5.0
SPARK_FILENAME=spark-$SPARK_VERSION-bin-hadoop3.tgz
SPARK_DIR="/opt/spark"

if $FORCE || [ ! -d "$SPARK_DIR" ]; then
  echo "🔥 Installing Apache Spark $SPARK_VERSION..."

  echo "🧹 Removing previous downloads..."
  rm -f $SPARK_FILENAME

  echo "🌐 Downloading Spark..."
  wget -O $SPARK_FILENAME https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/$SPARK_FILENAME

  echo "📂 Extracting Spark..."
  tar xvf $SPARK_FILENAME || { echo "❌ Extraction failed. Check your download."; exit 1; }

  if [ -d "$SPARK_DIR" ]; then
    echo "🚮 Removing existing Spark directory..."
    sudo rm -rf "$SPARK_DIR"
  fi

  echo "🚚 Moving Spark to /opt..."
  sudo mv spark-$SPARK_VERSION-bin-hadoop3 $SPARK_DIR
  rm $SPARK_FILENAME
else
  echo "🧊 Spark already exists. Use --force to reinstall."
fi

# 🧠 Add env vars to .bashrc if not already present
if ! grep -q "SPARK_HOME" "$HOME/.bashrc"; then
cat << 'EOF' >> "$HOME/.bashrc"

# ⚙️ Spark + Java environment variables
export SPARK_HOME=/opt/spark
export JAVA_HOME=$HOME/.sdkman/candidates/java/current
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
EOF
fi

echo "💻 Installing Databricks CLI..."
python3 -m pip install --upgrade pip
python3 -m pip install databricks-cli

echo "🐍 Installing PySpark..."
python3 -m pip install pyspark

echo "📓 Installing Jupyter Notebook & JupyterLab..."
python3 -m pip install notebook jupyterlab


echo "[JUPYTER] Creating Jupyter startup hook for Spark env vars..."

mkdir -p ~/.ipython/profile_default/startup

cat << 'EOF' > ~/.ipython/profile_default/startup/00-spark-env.py
import os

# Inject environment variables so PySpark runs in notebooks without manual setup
os.environ["JAVA_HOME"] = os.path.expanduser("~/.sdkman/candidates/java/current")
os.environ["SPARK_HOME"] = "/opt/spark"
EOF

echo "[JUPYTER] Auto-env injection added for notebooks (JAVA_HOME + SPARK_HOME)."


# 🔐 Set Jupyter password
JUPYTER_PASSWORD="edfi"  # 👈 Change this if needed

echo "[JUPYTER] Setting default notebook password..."

python3 - <<EOF
try:
    from notebook.auth import passwd  # Older versions
except ImportError:
    from jupyter_server.auth import passwd  # Jupyter 7+

import os, json

hashed = passwd("$JUPYTER_PASSWORD")
config_path = os.path.expanduser("~/.jupyter/jupyter_notebook_config.json")
os.makedirs(os.path.dirname(config_path), exist_ok=True)

with open(config_path, "w") as f:
    json.dump({"NotebookApp": {"password": hashed}}, f)

print(f"[JUPYTER] Password written to {config_path}")
EOF


echo "
🧪 Jupyter Notebook Password Setup Complete

🔑 Default password: $JUPYTER_PASSWORD

You can change it later anytime with:
    jupyter notebook password

To launch Jupyter:
    jupyter notebook --no-browser --ip=127.0.0.1 --port=8888
"




echo "🧪 Writing PySpark verification script..."
cat << 'EOF' > ./scripts/test_pyspark_read.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Verify CSVs with Spark").getOrCreate()

try:
    print("📘 Reading edfi_school.csv...")
    school_df = spark.read.option("header", "true").csv("edfi_school.csv")
    school_df.show(5)

    print("📗 Reading edfi_student.csv...")
    student_df = spark.read.option("header", "true").csv("edfi_student.csv")
    student_df.show(5)

    print("📙 Reading edfi_studentschoolassociation.csv...")
    assoc_df = spark.read.option("header", "true").csv("edfi_studentschoolassociation.csv")
    assoc_df.show(5)
except Exception as e:
    print(f"❌ CSV read test failed: {e}")
finally:
    spark.stop()
EOF

echo "🚀 Running PySpark verification..."
python3 ./scripts/test_pyspark_read.py || echo "⚠️ CSV test failed. Are your files in the current directory?"

echo "🧼 Final cleanup..."
sudo apt-get autoremove -y && sudo apt-get clean

echo "🐳 Installing Docker & Docker Compose..."

# Install Docker
if ! command -v docker &> /dev/null; then
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -y
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
else
  echo "✅ Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
  sudo apt-get install -y docker-compose
else
  echo "✅ Docker Compose already installed"
fi

# Add user to docker group (no sudo needed)
sudo usermod -aG docker $USER

echo "🧃 Docker installed. You may need to restart your WSL session or run: newgrp docker"


echo "
✅ INSTALLATION COMPLETE

📦 Java 16
📦 Python 3
📦 Apache Spark $SPARK_VERSION
📦 Databricks CLI
📦 PySpark
📦 Jupyter Notebook + JupyterLab
📦 Docker
🧪 CSV Read Test

📚 To start Jupyter Notebook:
    cd ~/your/project/path
    jupyter notebook --no-browser --ip=127.0.0.1 --port=8888

📚 Or to use the modern interface:
    jupyter lab

💡 Tip: Paste the full URL from the terminal into your browser on Windows

♻️ To reload your shell with Spark and Java:
    source ~/.bashrc

🛠 Re-run with:
    ./setup/install_and_verify_wsl_tools.sh --force
to reinstall Spark from scratch.

📄 Heads up: If WSL keeps launching into \`root@...\`, you're living that dangerous root life™.

This can break tools like Jupyter, SDKMAN, and more.

📘 Fix it with this quick guide:
    /docs/fix-wsl-root-readme.md

🛠 After installation, don’t forget to apply the Docker group change without rebooting WS
    newgrp docker
"