FROM ubuntu:16.04

# Needed for better experience in container terminal
ENV TERM=xterm-256color

# Update and install
RUN apt-get update && apt-get install -y \
      git \
      wget \
      # Python
      python3-dev \
      python3-pip \
      # Some linux visulization package
      libgtk-3-0 \
      libpng12-0 \
      libjpeg-dev \
      libtiff-dev \
      libxxf86vm1 \
      libxxf86vm-dev \
      libxi-dev \
      libxrandr-dev \
      libsdl-dev \
      libnotify-dev \
      libsm-dev 

RUN /bin/bash -c 'pip3 install --upgrade pip'
RUN /bin/bash -c 'pip3 install --default-timeout=1000 -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04/ wxPython'
RUN /bin/bash -c 'pip3 install matplotlib seaborn numpy scipy pandas scikit-learn'

COPY . /src
WORKDIR /src/dshelper

CMD ["python3", "dshelper.py"]