FROM python:3.11

# Install pipenv
RUN pip install pipenv

WORKDIR /app

# Copy Pipfile and install dependencies
COPY Pipfile .
RUN pipenv install --deploy

# Copy the application
COPY . /app

# Command to run the bot
CMD ["pipenv", "run", "python", "main.py"]