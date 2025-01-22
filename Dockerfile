FROM python:3.11

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

# Copy Pipfile and install dependencies
COPY Pipfile .
RUN pipenv install --deploy

# Copy JavaScript dependencies files and install
COPY snapshot/package*.json /app/snapshot/
RUN cd /app/snapshot && npm install

# Copy the entire application
COPY . /app

# Create an entrypoint script with proper wait for database
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for database..."\n\
while ! nc -z db 5432; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
sleep 5\n\
echo "Initializing database..."\n\
cd /app && pipenv run python -m scripts.init_db && \\\n\
echo "Starting application..." && \\\n\
pipenv run python main.py' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Install netcat for database connection check
RUN apt-get install -y netcat-openbsd

CMD ["/app/entrypoint.sh"]