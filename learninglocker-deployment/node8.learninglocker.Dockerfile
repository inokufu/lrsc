ARG NODE_VERSION=8-slim
ARG PLATFORM=linux/amd64

FROM --platform=${PLATFORM} node:${NODE_VERSION} AS builder

RUN echo "Updating Sources" \
    && sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list \
    && sed -i 's|security.debian.org|archive.debian.org/|g' /etc/apt/sources.list \
    && sed -i '/stretch-updates/d' /etc/apt/sources.list

RUN echo "Updating Packages" \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --allow-unauthenticated --assume-yes --no-install-recommends \
        curl \
        git \
        ca-certificates \
        python \
        build-essential \
        xvfb \
        apt-transport-https \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*

RUN echo "Installing yarn" \
    && npm install -g --force yarn

RUN echo "Cloning Learning Locker" \
    && git clone --branch v7.1.1 --depth 1 --single-branch \
    https://www.github.com/LearningLocker/learninglocker /opt/learninglocker

WORKDIR /opt/learninglocker

RUN echo "Building Services" \
    && npm_config_build_from_source=true yarn install --ignore-engines \
    && yarn build-all

FROM --platform=${PLATFORM} node:${NODE_VERSION}

RUN echo "Updating Sources" \
    && sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list \
    && sed -i 's|security.debian.org|archive.debian.org/|g' /etc/apt/sources.list \
    && sed -i '/stretch-updates/d' /etc/apt/sources.list

RUN echo "Updating Packages" \
    && apt-get update -y && apt-get install -y --no-install-recommends \
        curl \
        xvfb \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/*

WORKDIR /opt/learninglocker

COPY --from=builder /opt/learninglocker /opt/learninglocker
