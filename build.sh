#!/bin/bash

# arguments:
# "dev" - create the python virtualenv and build the PG package in edit mode
# "prod" - git tag, deploy the PG package from tagged version

# see install_pyenv.sh to install pyenv or https://realpython.com/intro-to-pyenv/

echo -e "Enter \"dev\" or \"prod\" for package build: "
read VAR

if [[ $VAR == "dev"* ]]; then

    echo -e "We need to install and compile Python. Prepare for more boredom... \n\n"

    pyenv_version=$( head -n 1 ./.python-version ) # get the prod version for local dev
    pyenv install $pyenv_version
    python_version=$( python -V )
    echo -e "Current Python version is $python_version ...\n"

    pip install --upgrade pip
    pip install pipx
    pipx ensurepath
    pipx install poetry

    poetry env remove python
    poetry install sync # only install necessary deps

    echo -e "The Patron Groups package has now been installed locally. \n"
    echo -e "See the README for more information about using this for development.\n\n"

elif [[ $VAR == "prod"* ]]; then

    source ~/.profile

    echo "Deploying the Patron Groups package... "

    # pull latest tag and checkout
    git fetch --tags
    latest_tag=$( git describe --tags `git rev-list --tags --max-count=1` )
    git checkout $latest_tag

    poetry build

    # get version from pyproject.toml
    version_line=$( sed '3q;d' ./pyproject.toml )
    regex="^version = ['\"]([^'\"]*)['\"]"

    if [[ $version_line =~ $regex ]]; then # bash native regex matching, doesn't need grep/sed

        echo "Upgrading pip first..."
        pip install --upgrade pip

        version_string="${BASH_REMATCH[1]}"
        echo -e "Current package version is ${version_string} \n\n"
        # uninstall old petal package
        pip uninstall -y petal
        pip uninstall -y patron_groups
	    pip install "$(pwd)/dist/patron_groups-${version_string}.tar.gz"
        # remove dist directory
        rm -rf ./dist

        echo -e "Installation of patron_groups-${version_string} completed.\n\n"

    else

        echo -e "A version number could not be found. Please check pyproject.toml for version information. Exiting...\n\n"
        exit 1

    fi

else

    echo "Usage: enter \"dev\" to build local virtualenv or \"prod\" to build tagged version... \n"

fi
