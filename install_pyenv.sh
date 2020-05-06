#!/bin/bash

echo -e "\n\nThis script helps install pyenv on your computer (Debian or MacOS)... \n\n"

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

elif [[ "$OSTYPE" == "linux-musl"* ]]; then # Alpine Linux
    apk add libffi-dev ncurses-dev openssl-dev readline-dev \
        tk-dev xz-dev zlib-dev

else
    echo -e "Sorry, the script can't find your OS type... \n"
    echo -e "Please use the directions from https://realpython.com/intro-to-pyenv/ to install pyenv to your computer. \n\n"
    exit 1
fi

curl https://pyenv.run | bash

# add pyenv scripting to user profile (this is portable across zsh bash etc. - hopefully)
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.profile
echo 'export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"' >> ~/.profile

exec "$SHELL"