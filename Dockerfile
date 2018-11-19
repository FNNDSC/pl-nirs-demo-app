# Docker file for the nirs_demo_app plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-nirs-demo-app .
#
# In the case of a proxy (located at 192.168.13.14:3128), do:
#
#    docker build --build-arg http_proxy=http://192.168.13.14:3128 --build-arg UID=$UID -t local/pl-nirs-demo-app .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --rm --entrypoint /bin/bash local/pl-nirs-demo-app
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti --rm -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-nirs-demo-app
#

FROM nvidia/cuda:10.0-devel-ubuntu18.04 as builder

WORKDIR /usr/src/mcx/build
COPY ["mcx", "/usr/src/mcx"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget python3 python3-pip &&  \
    wget -q https://cmake.org/files/v3.12/cmake-3.12.3-Linux-x86_64.sh  &&  \
    mkdir /usr/cmake                                                    &&  \
    sh cmake-3.12.3-Linux-x86_64.sh --skip-license --prefix=/usr/cmake  &&  \
    ln -s /usr/cmake/bin/cmake /usr/bin/cmake                           &&  \
    pip3 install setuptools wheel                                       &&  \
    cmake ..                                                            &&  \
    make pymcx

FROM python:3-slim
MAINTAINER fnndsc "dev@babymri.org"

LABEL com.nvidia.volumes.needed="nvidia_driver"
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

ENV APPROOT="/usr/src/nirs_demo_app"  VERSION="0.1"
COPY ["nirs_demo_app", "${APPROOT}"]
COPY ["requirements.txt", "${APPROOT}"]
COPY --from=builder ["/usr/src/mcx/build/pymcx", "${APPROOT}/pymcx"]

WORKDIR $APPROOT

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python3"]
CMD ["nirs_demo_app.py", "--json"]
