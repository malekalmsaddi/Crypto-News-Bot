# Stage 1: Build base with Python
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy required files
COPY main.py /app/
COPY shared.py /app/
COPY webhook.py /app/
COPY admin_ui.py /app/
COPY bot.py /app/
COPY config.py /app/
COPY models.py /app/
COPY database.py /app/
COPY requirements.txt /app/
COPY market.py /app/
COPY state.py /app/
COPY logging_config.py /app/
COPY broadcast_to_all.py /app/
COPY add_group_link.py /app/
COPY add_new_command.py /app/
COPY register_commands.py /app/
COPY setup_group.py /app/

# Copy folders
COPY static/ /app/static/
COPY attached_assets/ /app/attached_assets/
COPY templates/ /app/templates/
RUN echo "🔍 TEMPLATES:" && ls -la /app/templates

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Fly.io
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]
RUN echo "Listing /app/templates:" && ls -la /app/templates

