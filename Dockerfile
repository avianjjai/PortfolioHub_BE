# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install LaTeX and required packages
# This installs a minimal TeX Live distribution with pdflatex
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-english \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Using --root-user-action=ignore to suppress warning (this is fine in Docker)
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for running the application
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user before running (security best practice)
USER appuser

# Expose port (Render will set PORT env var)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
