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

# Command to run the application
CMD ["pipenv", "run", "python", "main.py"]
