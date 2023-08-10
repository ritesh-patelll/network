FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /network

# Copy requirements.txt BEFORE running pip install
COPY requirements.txt /network/

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application's code
COPY . /network/