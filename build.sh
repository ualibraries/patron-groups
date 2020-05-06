#!/bin/bash

# arguments:
# "dev" - create the python virtualenv and build the PG package in edit mode
# "prod" - git tag, deploy the PG package from tagged version

# see install_pyenv.sh to install pyenv or https://realpython.com/intro-to-pyenv/


echo -n "Enter \"dev\" or \"prod\" for package build: "
read VAR

function git_install_tag {
    latest_tag=$( git describe --tags `git rev-list --tags --max-count=1` )
    git fetch --tags
    git checkout $latest_tag
}

if [[ $VAR == "dev"* ]]; then
    pyenv_version=$( head -n 1 ./.python-version ) # get the prod version for local dev
    pyenv install $pyenv_version

    # create our virtualenv
    pyenv virtualenv pgrps-venv
    python_version=$( python -V )
    echo -e "Current Python version is $python_version ...\n"

    # upgrade pip
    pip install wheel # weird, pyenv's pip doesn't include this?
    pip install --upgrade pip

    # install package in dev mode
    echo -e "Installing the Patron Groups package in editable (dev) mode... \n"
    cd src/main/python
    pip install --trusted-host pypi.python.org -r requirements.txt
    pip install -e . # install editable package with dependencies

    echo -e "The Patron Groups package has now been installed locally. \n
            Run './run_petl_dev.sh' to test functionality.\n\n"

elif [[ $VAR == "prod"* ]]; then
    # TODO: WIP!!!
    # actual deployment of package to global pip

    echo "Deploying the Patron Groups package... "

    # # git pull last tag
    git_install_tag

    # install package in production
    cd src/main/python
    sudo pip3 install --trusted-host pypi.python.org -r requirements.txt
    python3 setup.py sdist # creates distribution package

    # get version from src/petal/__init__.py::__version__
    # pgrps_version=$( grep -oP "^__version__ = ['\"]([^'\"]*)['\"]" ./src/petal/__init__.py )
    # pip install absolute path to PG package

else
    echo "Usage: enter \"dev\" to build local virtualenv or \"prod\" to build tagged version... \n"

fi
