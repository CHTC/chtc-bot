#!/usr/bin/env bash

tag=$1
docker build -t "${tag}" -f docker/Dockerfile .
docker push "${tag}"
