ARG BUILD_FROM=hassioaddons/ubuntu-base:5.0.1
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base system
ARG BUILD_ARCH=amd64
ENV LANG C.UTF-8
RUN \
    apk add --no-cache python3 \
    \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install "colorama==0.3.7" "requests==2.18.4" "beautifulsoup4==4.8.1" "paho_mqtt==1.4.0" "pyyaml"

COPY Run.sh /run.sh
COPY Rika_firenet_beta.py /
RUN chmod a+x /run.sh
RUN chmod a+x /Rika_firenet_beta.py

WORKDIR /
CMD [ "/run.sh" ]
