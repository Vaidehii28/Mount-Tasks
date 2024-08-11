#!/usr/bin/env bash
# Install system dependencies for WeasyPrint
apt-get update && apt-get install -y \
libpango1.0-dev \
libffi-dev \
libxml2-dev \
libxslt1-dev \
libjpeg-dev \
zlib1g-dev
