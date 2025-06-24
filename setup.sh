#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pip install --upgrade pip
pip install -r "${SCRIPT_DIR}/requirements.txt"
pip install .
mkdir commons-ip
wget -O commons-ip/commons-ip2-cli-2.10.0.jar https://github.com/keeps/commons-ip/releases/download/2.10.0/commons-ip2-cli-2.10.0.jar
