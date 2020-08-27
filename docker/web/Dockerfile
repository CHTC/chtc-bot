FROM python:3.8

# build config
ARG HTCONDOR_VERSION=8.9

# environment setup
ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

# install utils and dependencies
# install HTCondor version specified in config
RUN : \
    && apt-get update \
    && apt-get -y install --no-install-recommends vim less git gnupg wget ca-certificates locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && wget -qO - https://research.cs.wisc.edu/htcondor/debian/HTCondor-Release.gpg.key | apt-key add - \
    && echo "deb http://research.cs.wisc.edu/htcondor/debian/${HTCONDOR_VERSION}/buster buster contrib" >> /etc/apt/sources.list.d/htcondor.list \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends htcondor \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "tiger.py"]
