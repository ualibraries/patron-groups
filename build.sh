#!/bin/bash

# arguments:
# "dev" - create the python virtualenv and build the PG package in edit mode
# "prod" - git tag, deploy the PG package from tagged version

# see install_pyenv.sh to install pyenv or https://realpython.com/intro-to-pyenv/


echo -n "Enter \"dev\" or \"prod\" for package build: "
read VAR

function git_install_tag {
    latest_tag = $(git describe --tags `git rev-list --tags --max-count=1`)
    git fetch --tags
    git checkout $latest_tag
}

if [[ $VAR == "dev"* ]]; then
    # update source from github
    git pull

    pyenv_version = $( head -n 1 ./.python-version ) # get the prod version for local dev
    pyenv install $pyenv_version

    # get the virtualenv and set python version
    pyenv virtualenvwrapper_lazy

    # make virtual environment available
    mkvirtualenv venv
    echo -e "Current Python version is ${ python -v } ...\n"

    # install package in dev mode
    echo -e "Installing the Patron Groups package in editable mode... \n"
    cd src/main/python
    pip install -e . # install editable package with dependencies

elif [[ $VAR == "prod"* ]]; then
    # TODO: WIP
    # actual deployment of package to global pip

    echo "Deploying the Patron Groups package... "

    # git pull last tag and match with package version
    git_install_tag

    # install package in production
    cd src/main/python
    python setup.py sdist # creates distribution package, version from src/petal/__init__.py::__version__

    # pip install absolute path to PG package

else
    echo "Usage: enter \"dev\" to build local virtualenv or \"prod\" to deploy tagged version... \n"

fi
