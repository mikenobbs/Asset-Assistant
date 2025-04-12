FROM python:3.11-slim-buster
ARG BRANCH_NAME=master
ENV BRANCH_NAME=${BRANCH_NAME}
ENV TINI_VERSION=v0.19.0
ENV PROCESSDIR=/config/process
ENV SHOWSDIR=/config/shows
ENV MOVIESDIR=/config/movies
ENV COLLECTIONSDIR=/config/collections
ENV FAILEDDIR=/config/failed
ENV BACKUPDIR=/config/backup
ENV LOGSDIR=/config/logs
ENV ENABLE_BACKUP_SOURCE=false
ENV ENABLE_BACKUP_DESTINATION=false
ENV SERVICE=
ENV PLEX_SPECIALS=
ENV COMPRESS_IMAGES=false
ENV IMAGE_QUALITY=85
ENV DEBUG=false
ENV PUID=1000
ENV PGID=1000

COPY requirements.txt requirements.txt
RUN echo "**** install system packages ****" \
 && apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && apt-get install -y tzdata --no-install-recommends \
 && apt-get install -y gcc g++ libxml2-dev libxslt-dev libz-dev libjpeg62-turbo-dev zlib1g-dev wget curl nano \
 && wget -O /tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-"$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
 && chmod +x /tini \
 && pip3 install --no-cache-dir --upgrade --requirement /requirements.txt \
 && apt-get --purge autoremove gcc g++ libxml2-dev libxslt-dev libz-dev -y \
 && apt-get clean \
 && apt-get update \
 && apt-get check \
 && apt-get -f install \
 && apt-get autoclean \
 && rm -rf /requirements.txt /tmp/* /var/tmp/* /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -g ${PGID} appuser \
 && useradd -u ${PUID} -g appuser -s /bin/bash -m appuser

# Create directories and set proper permissions
RUN mkdir -p /config /config/process /config/shows /config/movies /config/collections /config/failed /config/backup /config/logs \
 && chown -R appuser:appuser /config

# Copy default config.yml to the app directory (will be copied to volume by entrypoint script)
COPY --chown=appuser:appuser config.yml /app/config.yml.default

# Copy entrypoint script
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy application files
COPY --chown=appuser:appuser . /app

# Set working directory
WORKDIR /app

# Switch to the non-root user
USER appuser

VOLUME /config
ENTRYPOINT ["/tini", "-s", "/entrypoint.sh", "python3", "/app/asset-assistant.py"]
