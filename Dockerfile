FROM python:3.11

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /bloomdiscordbot

# Copy only Pipfile (ignore Pipfile.lock)
COPY Pipfile .

# Install python dependencies in /.venv
RUN pipenv install --deploy

# Copy package.json and package-lock.json (if available)
COPY snapshot/package*.json ./snapshot/

# Install JavaScript dependencies
RUN cd snapshot && npm install

# Create a volume directory
VOLUME /main/data

# Install application into container
COPY . .

# Run the Python script to modify the JSON file
RUN pipenv run python update-script.py

# Run the application
CMD pipenv run python main.py
# CMD ["pipenv", "run", "python", "main.py"]