# pull official base image
FROM python:3.8-alpine

# set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# set work directory
WORKDIR /django

# install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /django/entrypoint.sh
RUN chmod +x /django/entrypoint.sh

# copy project
COPY . .

# run entrypoint
ENTRYPOINT ["/django/entrypoint.sh"]