FROM debian:11
FROM python:3.10.4-slim-buster

WORKDIR /YutaRobot/

RUN apt-get update && apt-get upgrade -y
RUN apt-get -y install git
RUN python3.10 -m pip install -U pip
RUN apt-get install -y wget python3-pip curl bash neofetch ffmpeg software-properties-common
RUN apt-get install -y --no-install-recommends ffmpeg

COPY requirements.txt .

RUN pip3 install wheel
RUN pip3 install --no-cache-dir -U -r requirements.txt

COPY . .
CMD ["python3.10", "-m", "YutaRobot"]
