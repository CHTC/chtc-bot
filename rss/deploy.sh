#!/bin/bash
rm -fr ./lambda/libs
mkdir ./lambda/libs
pip install --requirement ./lambda/requirements.txt --target ./lambda/libs

sam validate

if [ ! -f samconfig.toml ]; then
    sam deploy -g
else
    sam deploy
fi
