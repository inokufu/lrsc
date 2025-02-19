# Use the official Node.js image as base image
FROM node:lts-slim

# Install pnpm globally, and install git
RUN apt-get update \
    && apt-get install -y git gettext-base \
    && npm install -g pnpm

# Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Clone the repository
RUN git clone --branch feat/https-configuration --depth 1 --single-branch https://github.com/inokufu/dataspace-connector.git .

# Copy the .env and config.json file
COPY .env.production .env.production
COPY config.production.json src/config.production.template.json
RUN set -a && . ./.env.production && set +a \
    && envsubst < src/config.production.template.json > src/config.production.json

# Install app dependencies
RUN CI=true pnpm i

RUN npm run build
