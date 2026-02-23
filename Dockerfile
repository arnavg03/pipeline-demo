FROM python:3.9-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the container
COPY . .

# Make the bash script executable
RUN chmod +x src/scripts/preprocess.sh

# Run the bash script
CMD ["./src/scripts/preprocess.sh"]