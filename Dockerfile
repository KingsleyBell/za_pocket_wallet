FROM python:3.6
ADD ./app /app
ADD ./requirements.txt /app/requirements.txt

# upgrade pip and install required python packages
RUN pip install -U pip
RUN pip install -r /app/requirements.txt

WORKDIR /app
EXPOSE 8002
CMD ["gunicorn", "-b", "0.0.0.0:8002", "app"]


