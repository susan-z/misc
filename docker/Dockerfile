FROM --platform=linux/amd64 ubuntu:22.04

LABEL org.opencontainers.image.source="https://github.com/SOURCE"
LABEL org.opencontainers.image.description="Base container image"

ENV UDEV=1

# Install the packages required by build process
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    autoconf \
    automake \
    bash-completion \
    bc \
    binutils \
    build-essential \
    ca-certificates \
    cmake \

ENV HOME=/home
ENV PYTHONPATH "${PYTHONPATH}:/home/PATH"
ENV PYTHONPATH "${PYTHONPATH}:/__w/PATHWITHINCONTAINER"
ENV ENV_VAR=SOMEFILEPATH

# copy the dependencies file to the working directory
COPY ${ENV_VAR} ${HOME}

# install dependencies
RUN pip install -r ${HOME}/requirements.txt

CMD ["/bin/bash"]
