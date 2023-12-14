FROM python:3.10

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

WORKDIR /bot

# Copy only Pipfile (ignore Pipfile.lock)
COPY Pipfile .

# Install python dependencies in /.venv
RUN pipenv install --deploy

# Create a volume directory
VOLUME /main/data

# Install application into container
COPY . .

# Run the application
CMD pipenv run python main.py
# CMD ["pipenv", "run", "python", "main.py"]
