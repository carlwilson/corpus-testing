#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -d _site ]; then
    rm -rf _site
fi
mkdir _site
if [ -d site/CSIP ]; then
    rm -rf site/CSIP
fi
if [ -d site/SIP ]; then
    rm -rf site/SIP
fi
if [ -d site/DIP ]; then
    rm -rf site/DIP
fi
if [ -f site/index.html ]; then
    rm site/index.html
fi
eark-corpora
