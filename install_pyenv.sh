#!/bin/bash

echo -e "\n\nThis script helps install pyenv on your computer (Debian/Alpine/MacOS)... \n\n"
echo -e "It may take a while & you may have to answer some questions. Prepare yourself for boredom... \n\n"

function add_pyenv_path() {
    # add pyenv scripting to user profile (this is portable across zsh bash etc. - hopefully)
    echo -e "\n\n\n" >> ~/.profile

cat << 'eof' >> ~/.profile
# ===== BEGIN PYENV STUFF =====
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
# ===== END PYENV STUFF =====
eof

    source ~/.profile
}

# load all the ingredients to install pyenv
if [[ "$OSTYPE" == "linux-gnu"* ]]; then # Debian Linux

    echo -e "Installing OS dependencies... \n\n"
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
        libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

elif [[ "$OSTYPE" == "darwin"* ]]; then # MacOS

    echo -e "Installing brew dependencies... \n\n"
    brew update
    brew install openssl readline sqlite3 xz zlib

elif [[ "$OSTYPE" == "linux-musl"* ]]; then # Alpine Linux

    echo -e "Installing OS dependencies... \n\n"
    apk add libffi-dev ncurses-dev openssl-dev readline-dev \
        tk-dev xz-dev zlib-dev

else

    echo -e "Sorry, the script can't find your OS type... \n"
    echo -e "Please use the directions from https://realpython.com/intro-to-pyenv/ to install pyenv to your computer. \n\n"
    exit 1

fi

if [[ ! -d ~/.pyenv ]]; then

    curl https://pyenv.run | bash

else

    echo -e "\n\nPyenv seems to have already been installed before. Please check pyenv documentation for installation details.\n"
    echo -e "If you wish to install again, please delete '~/.pyenv' and any pyenv lines from your shell profile.\n\n"
    exit 1

fi

# check for user shell profile
if [[ ! -f ~/.profile ]]; then

    if [ touch ~/.profile ]; then
	add_pyenv_path
	echo -e "User .profile added to shell configuration.\n\n"
    else
	# try to create the .profile or give user hints
        echo -e "Please create a user .profile and append the following lines to user .bashrc or .zshrc... \n\n"
        cat >> 'ADDLINES'
            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init -)"
            eval "$(pyenv virtualenv-init -)"
            export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV="true"
        ADDLINES
        exit 1
    fi
    
else

    add_pyenv_path

fi

# restart the session to reload user environment - WARNING: nothing will run after this line!
exec $SHELL -l

