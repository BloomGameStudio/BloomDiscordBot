FROM python:3.11

RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

WORKDIR /app

COPY Pipfile .
RUN pipenv install --deploy

COPY . /app
RUN npm install

CMD ["pipenv", "run", "python", "main.py"]