FROM ubuntu:16.04

RUN apt-get update && \
    apt-get -y install git build-essential \
                    python3 \
                    python3-dev \
                    python3-pip && \
    pip3 install --upgrade pip 

COPY . /opt/hasker/
RUN pip3 install -r /opt/hasker/requirements.txt

EXPOSE 8000
