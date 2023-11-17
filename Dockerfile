ARG PYTHON_VERSION=3.11.6
ARG DEBIAN_VERSION=bullseye

FROM python:${PYTHON_VERSION}-slim-${DEBIAN_VERSION}
LABEL maintainer=blake.dewey@jhu.edu
ARG PYTHON_VERSION
ARG DEBIAN_VERSION

ENV PYTHONUSERBASE=/opt/python

RUN apt-get update && \
    apt-get -y --no-install-recommends install ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

# Create manifest json file
RUN echo -e "{\n \
    \"PYTHON_VERSION\": \"${PYTHON_VERSION}\",\n \
    \"DEBIAN_VERSION\": \"${DEBIAN_VERSION}\"\n \
}" > /opt/manifest.json

# Copy package and install
COPY . /tmp/ghactionstest-src/
RUN cd /tmp/ghactionstest-src/ && git describe --long --always
RUN pip install --no-cache-dir /tmp/ghactionstest-src/ && \
    rm -rf /tmp/ghactionstest-src/

ENTRYPOINT ["python"]
