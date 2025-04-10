# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    # Add the local user's bin directory to PATH
    PATH="/home/appuser/.local/bin:$PATH"

# Create a non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

# Set working directory
WORKDIR /opt/emon_tools

# Install build dependencies if needed (e.g., for any compiled packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    dos2unix \
    default-mysql-client \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them as the non-root user
COPY --chown=appuser:appuser requirements-docker-dev.txt .

# Create the datas and static directories for storing data
RUN mkdir -p /opt/emon_tools/datas /opt/emon_tools/static  /opt/emon_tools/backend \
    && chown -R appuser:appuser /opt/emon_tools/datas /opt/emon_tools/static /opt/emon_tools/backend

# Switch to the non-root user
USER appuser

# Upgrade pip
Run python3.11 -m pip install --no-cache-dir --user --upgrade pip

# Install Python dependencies
# Use --no-cache-dir to avoid caching the packages in the image
# Use --user to install packages in the user's home directory
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user -r requirements-docker-dev.txt

# Copy the backend source code
COPY --chown=appuser:appuser . ./backend

COPY --chown=appuser:appuser .env.docker ./backend/.env

RUN dos2unix /opt/emon_tools/backend/scripts/docker_start.sh
RUN dos2unix /opt/emon_tools/backend/scripts/pre_start.sh
RUN dos2unix /opt/emon_tools/backend/scripts/wait-for-db.sh

# Ensure scripts have execution permission
RUN chmod +x /opt/emon_tools/backend/scripts/docker_start.sh \
    && chmod +x /opt/emon_tools/backend/scripts/pre_start.sh \
    && chmod +x /opt/emon_tools/backend/scripts/wait-for-db.sh

# Set the PYTHONPATH to ensure the backend module is found
ENV PYTHONPATH=/opt/emon_tools

# Expose FastAPI port (use 8000)
EXPOSE 8000

# Use the entrypoint script as CMD, which will run migrations and then launch uvicorn
CMD ["./backend/scripts/docker_start.sh"]