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

    # create our virtualenv
    pyenv virtualenv pgrps-venv
    python_version=$( python -V )
    echo -e "Current Python version is $python_version ...\n"

    # upgrade pip (note this is local pip, not using pip3 alias)
    pip install wheel # weird, pyenv's pip doesn't include wheel?
    pip install --upgrade pip # this can get out of date

    # install petal package in dev mode
    echo -e "Installing the Patron Groups package in editable (dev) mode... \n"
    cd src/main/python
    pip install --trusted-host pypi.python.org -r requirements.txt
    pip install -e . # install editable package with dependencies

    echo -e "The Patron Groups package has now been installed locally. \n"
    echo -e "See the README for more information about using this for development.\n\n"

elif [[ $VAR == "prod"* ]]; then

    # TODO: WIP!!!
    # actual deployment of package to global python3/pip3 production environment

    echo "Deploying the Patron Groups package... "

    # pull latest tag and checkout
    latest_tag=$( git describe --tags `git rev-list --tags --max-count=1` )
    git fetch --tags
    git checkout $latest_tag

    # we'll always run reqs install in case they change
    cd src/main/python
    sudo pip3 install --trusted-host pypi.python.org -r requirements.txt
    python3 setup.py sdist # create regular distribution package

    # get version from src/petal/__init__.py::__version__
    version_line=$( head -n 1 ./src/petal/__init__.py )
    regex="^__version__ = ['\"]([^'\"]*)['\"]"

    if [[ $version_line =~ $regex ]]; then # bash native regex matching, doesn't need grep/sed
        
        version_string="${BASH_REMATCH[1]}"
        echo -e "Current package version is ${version_string} \n\n"
        # uninstall old petal package
        sudo pip3 uninstall petal
        # deploy new petal
	sudo pip3 install "$(pwd)/dist/petal-${version_string}.tar.gz"
        # remove dist directory
        rm -rf ./dist

        echo -e "Installation of petal-${version_string} completed.\n\n"

    else

        echo -e "A version number could not be found. Please check src/petal/__init__.py for version information. Exiting...\n\n"
        exit 1
        
    fi

else

    echo "Usage: enter \"dev\" to build local virtualenv or \"prod\" to build tagged version... \n"

fi
