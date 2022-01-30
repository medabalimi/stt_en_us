FROM ubuntu:20.04

RUN apt-get update && ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y rabbitmq-server supervisor \
    python3-dev python3-pip \
    ffmpeg libsndfile1-dev

RUN mkdir -p /opt/stt/mount

ADD . /opt/stt

WORKDIR /opt/stt
RUN python3 -m pip install setuptools==59.5.0
RUN python3 -m pip install -r requirements.txt


RUN cp supervisor.d/rabbitmq.conf /etc/supervisor/conf.d
RUN cp supervisor.d/stt_api.conf /etc/supervisor/conf.d
RUN cp supervisor.d/supervisord.conf /etc/supervisor/conf.d
RUN python3 download_models.py
CMD ["/usr/bin/supervisord"]
