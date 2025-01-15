FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y gcc openssl-devel bzip2-devel libffi-devel wget unzip libuuid expat
# Download and unzip headless chromium, then clean up the zip file
RUN wget https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017-03.zip && \
    unzip stable-headless-chromium-amazonlinux-2017-03.zip && \
    rm stable-headless-chromium-amazonlinux-2017-03.zip && \
    chmod +x headless-chromium \

RUN yum -y update && \
    yum install -y \
        gcc \
        gcc-c++ \
        make \
        pango \
        cairo \
        libffi \
        libgcc \
        libstdc++ \
        pkgconfig \
        freetype-devel \
        fontconfig-devel \
        cairo-devel \
        pango-devel \
        meson \
        ninja-build \
        tar \
        gzip \
        bzip2 \
        perl \
        which \
        xz \
    && yum clean all

WORKDIR /var/task/


COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py .
COPY builders.py .
COPY __init__.py .
COPY assets/ assets/
COPY templates/ templates/

ENV PYPPETEER_HOME=/tmp/
ENV FONTCONFIG_PATH=/var/task/fonts
ENV CHROME_PROFILE_PATH=/tmp/
ENV LD_LIBRARY_PATH=/var/task/lib
ENV CHROME_EXECUTABLE_PATH=/var/task/headless-chromium


CMD ["app.handler"]
