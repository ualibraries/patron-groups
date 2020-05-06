#!/bin/bash

echo -e "This script helps install pyenv on your computer (Debian or MacOS)... "
echo -e "You'll be asked to add a few lines to your shell profile when done... \n\n"

sleep 7 # give folks time to read...

# load all the ingredients to install pyenv
if [[ "$OSTYPE" == "linux-gnu"* ]]; then # Debian Linux
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
        libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

elif [[ "$OSTYPE" == "darwin"* ]]; then # MacOS
    echo -e "Installing brew dependencies... \n\n"
    brew update
    brew install openssl readline sqlite3 xz zlib

    # necessary to add headers for newer MacOS (>=10.14)
    sudo installer -pkg \
        /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg \
        -target /

elif [[ "$OSTYPE" == "linux-musl"* ]]; then # Alpine Linux
    apk add libffi-dev ncurses-dev openssl-dev readline-dev \
        tk-dev xz-dev zlib-dev

else
    echo -e "Sorry, the script can't find your OS type... \n"
    echo -e "Please use the directions from https://realpython.com/intro-to-pyenv/ to install pyenv to your computer. \n\n"
    exit 1
fi

curl https://pyenv.run | bash
