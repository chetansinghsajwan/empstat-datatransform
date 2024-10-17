FROM ubuntu:24.10

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y \
    python3 \
    faker \
    python3-pandas

WORKDIR /root/src
COPY . .

CMD [ "python3", "run.py" ]
