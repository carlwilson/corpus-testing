#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f ./config/runners.json ]; then
    rm ./config/runners.json
fi
cp ./config/eark-commons.json ./config/runners.json
eark-runner --clear
if [ -f ./config/runners.json ]; then
    rm ./config/runners.json
fi
cp ./config/eark-validator.json ./config/runners.json
pip install -r "${SCRIPT_DIR}/requirements_dev.txt"
eark-runner
