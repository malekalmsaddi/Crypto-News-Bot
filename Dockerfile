# Stage 1: Build base with Python
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy only required files explicitly
COPY main.py /app/
COPY shared.py /app/
COPY webhook.py /app/
COPY admin_ui.py /app/
COPY bot.py /app/
COPY config.py /app/
COPY models.py /app/
COPY database.py /app/
COPY requirements.txt /app/
COPY templates/ /app/templates/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Fly.io
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]
