# UAL Patron Groups

## Overview

The first piece is a small, quick [Python][python] hack that
synchronizes [LDAP][ldap] queries against UA's Enterprise
Directory Service ("EDS") into [Grouper][grouper] groups living in
UA's central Grouper service.  In the original use case, those
group memberships then show up as "isMemberOf" attributes in the
information returned from a successful [Shibboleth][shibboleth]
authentication; vendors running Shib-aware services can then use
the "isMemberOf" information to make authorization and access
control decisions.

Note that the general principle behind this project -- exposing the
complexity of "who gets access to what" as simple authorization
attributes based on group membership -- should hopefully be broadly
applicable to other use cases in the future.

## Setup

### Dev install, build, and testing

We want to avoid polluting our system-level Python environment, so we install a local
environment using [PyEnv][pyenv] and [PyEnv-Virtualenv][pyenv-virtualenv]. For now, this repo supports scripted installation of Pyenv on MacOS, Debian Linux, and Alpine Linux.

**This software assumes that we have Python3 and pip3 installed in both development and production environments.**

The required python version (as set in the production server) is found in the .python-version file in the root of the project. The python interpreter is only installed locally, and gets automagically used when the user's terminal session enters the project directory. *Therefore it is necessary to change directory into the project to later run development PG scripts.*

* Checkout the repo files and change directory into the project root.
* Install pyenv with `./install.sh`. This checks for Pyenv, installs if it's not there. It may also ask the user to update their shell profile to use pyenv.
* Build the virtual environment and add the Patron Groups package with `./build.sh`, enter "dev" at the prompt.
* Copy the .env_dist file to .env, then fill in the passwords with the correct credentials, probably located in Stache.
* Finally, test the scripts with `./run_petl_dev.sh`.

### Production

Production petl.library.arizona.edu will run the Patron Groups scripts daily with a cron job.

The production environment is different because it uses a global Python interpreter. Therefore, packages need to be updated using sudo permissions. There is no virtual environment to run the scripts from, and the `petal` package is "compiled" using the regular Python distribution. For this simple server setup, the user needs to SSH in to petl.library.arizona.edu.

* Change directory into `/usr/local/ual-patron-groups/`
* Run `./build.sh`, enter "prod" at the prompt.

## Maintainers

UA Libraries, TeSS-Dev Team




[python]: https://www.python.org/
[ldap]: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol
[grouper]: https://www.internet2.edu/products-services/trust-identity/grouper/
[shibboleth]: https://shibboleth.net/
[docker]: https://www.docker.com/
[alpine]: https://alpinelinux.org/
[crond]: https://en.wikipedia.org/wiki/Cron
[gradle]: https://gradle.org/
[homebrew]: https://brew.sh/
[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv
