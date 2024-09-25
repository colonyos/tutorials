FROM docker.io/tensorflow/tensorflow:2.13.0-gpu

RUN apt-get update && DEBIAN_FRONTEND="noninteractive" TZ="Europe/Stockholm" apt-get install -y python3 python3-pip wget git
RUN python3 -m pip install --upgrade pip
RUN pip3 install matplotlib geopandas matplotlib contextily openeo
