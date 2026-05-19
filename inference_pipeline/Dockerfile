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
RUN pip install pandas numpy pyarrow python-dotenv requests scikit-learn fastapi uvicorn

COPY common/ /app/common/
COPY inference_pipeline/ /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]