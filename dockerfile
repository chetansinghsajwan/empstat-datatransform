FROM ubuntu:24.10

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y \
    python3 \
    python3-pip

# RUN pip3 install pandas sqlalchemy
RUN apt-get install -y \
    faker \
    python3-pandas \
    python3-sqlalchemy \
    python3-dotenv \
    python3-psycopg2

WORKDIR /root/src
COPY . .

CMD [ "python3", "run.py" ]
