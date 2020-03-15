FROM python:2.7
MAINTAINER noredistribution

# Creating Application source code directory
RUN mkdir -p /ghcalert/src

# Setting Home Directory for containers
WORKDIR /ghcalert/src

# Installing python dependencies
COPY requirements.txt /ghcalert/src
RUN pip install --no-cache-dir -r requirements.txt

# Copying src code to Container
COPY . /ghcalert/src/app

# Application Environment variables
ENV APP_ENV development


# Exposing Ports
EXPOSE 5001

ENTRYPOINT ["python", "app/cvp_ghc_alerter.py", "--ghcURL"]
