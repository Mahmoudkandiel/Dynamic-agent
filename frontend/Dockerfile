# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy dependencies
#COPY requirements.txt .

# Install dependencies
RUN pip install streamlit

# Copy app code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
