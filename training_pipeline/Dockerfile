FROM python:3.11-slim

ENV PYTHONPATH=/app

# Install build tools needed for packages like twofish
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip wheel

# Install hopsworks
RUN pip install "hopsworks[python]==4.7.*"
RUN pip install pandas numpy pyarrow python-dotenv requests scikit-learn

COPY common/ /app/common/
COPY training_pipeline/ /app/

ENTRYPOINT ["python3", "main.py"]