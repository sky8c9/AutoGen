FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install --no-cache-dir -r requirements.txt python-multipart

COPY ./src ./src

COPY ./sample ./sample

COPY ./template ./template

WORKDIR src

ENTRYPOINT ["python", "web_server.py"]
