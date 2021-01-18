FROM ubuntu:20.10

# Needed for better experience in container terminal
ENV TERM=xterm-256color

# Disable interactive command
ENV DEBIAN_FRONTEND noninteractive

# Update and install
RUN apt-get update && apt-get install -y \
      git \
      wget \
      # Python
      python3-dev \
      python3-pip \
      # Some linux visulization package
      libgtk-3-0 \
      libpng-dev \
      libjpeg-dev \
      libtiff-dev \
      libxxf86vm1 \
      libxxf86vm-dev \
      libxi-dev \
      libxrandr-dev \
      libsdl-dev \
      libnotify-dev \
      libsm-dev \
      libsdl2-mixer-2.0-0 \
      libsdl2-image-2.0-0 \
      libsdl2-2.0-0

RUN /bin/bash -c 'pip3 install --upgrade pip'
RUN /bin/bash -c 'pip3 install --default-timeout=1000 -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04/ wxPython'

COPY . /src
WORKDIR /src/dshelper
COPY requirements.txt .
RUN /bin/bash -c 'pip3 install -r requirements.txt'

CMD ["python3", "main_gui.py"]
