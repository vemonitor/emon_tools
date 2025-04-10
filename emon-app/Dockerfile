# Use slim Node base image
FROM bitnami/node:latest

# Create non-root user
RUN useradd -m -u 1001 appuser

# Set working directory
WORKDIR /opt/app

# Copy package files first to leverage Docker cache
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /opt/app

# Switch to non-root user
USER appuser

# Expose Vite dev server port
EXPOSE 5173

# Start Vite in dev mode with hot reload
CMD [ "npm", "run", "dev", "--", "--host", "--port", "5173" ]