# UAL Patron Groups

## Overview

The software is a small, quick [Python][python] hack that synchronizes [LDAP][ldap] queries against UA's Enterprise Directory Service ("EDS") into [Grouper][grouper] groups living in UA's central Grouper service.  In the original use case, those group memberships then show up as "isMemberOf" attributes in the information returned from a successful [Shibboleth][shibboleth] authentication; vendors running Shib-aware services can then use the "isMemberOf" information to make authorization and access control decisions.

Note that the general principle behind this project -- exposing the complexity of "who gets access to what" as simple authorization attributes based on group membership -- should hopefully be broadly applicable to other use cases in the future.

## Setup

You have two ways to run this for development. Pick whichever fits your machine:

* **Option A – Local install** using [pyenv][pyenv] + [poetry][poetry] directly on your host. Fast iteration, but you have to have pyenv and poetry installed (or willing to install them).
* **Option B – Docker Compose** using the bundled `Dockerfile` + `compose.yml`. Your host only needs Docker; the container brings pyenv and poetry with it. Good if you don't want pyenv/poetry on your host (e.g. you use [uv][uv] instead).

Both options read credentials from a `.env` file in the project root, so in either case start by copying `.env_dist` to `.env` and filling in the passwords (probably located in Stache):

```shell
cp .env_dist .env
# then edit .env
```

### Option A – Dev install, build, and testing (local)

We want to avoid polluting our system-level Python environment, so we install a local
environment using [PyEnv][pyenv]. For now, this repo supports scripted installation of Pyenv on MacOS, Debian Linux, and Alpine Linux.

**This software assumes that we have Python3 and pip3 installed in both development and production environments.**

The required python version (as set in the production server) is found in the .python-version file in the root of the project. The python interpreter is only installed locally, and gets automagically used when the user's terminal session enters the project directory. *Therefore it is necessary to change directory into the project to later run development PG scripts.*

* Checkout the repo files and change directory into the project root.
* Install pyenv with `./install_pyenv.sh`. This checks for Pyenv, installs if it's not there. It may also ask the user to update their shell profile to use pyenv.
* Build the virtual environment and add the Patron Groups package with `./build.sh`, enter "dev" at the prompt.
* Copy the .env_dist file to .env, then fill in the passwords with the correct credentials, probably located in Stache.
* Test run the scripts with `./run_petl_dev.sh`. This script does not run the actual sync (--sync).
* When the development code is ready to be tagged, change the version in `pyproject.toml`. This property is referenced as the final package version when installed in production. It should be a [SemVer][semver] number format.

### Option B – Dev install, build, and testing (Docker Compose)

Instead of installing pyenv and poetry on your host, you can run everything inside a container. The included `Dockerfile` reproduces exactly what `./build.sh dev` does (installs pyenv, compiles the pinned CPython, installs poetry via pipx, runs `poetry sync`), and `compose.yml` wires up the common ways to use it.

Requirements:
* Docker Engine and the Compose plugin (`docker compose ...`, v2). Nothing else — no pyenv, no poetry, no matching Python version on the host.

Steps:

* Check out the repo files and change directory into the project root.
* Copy `.env_dist` to `.env` and fill in the passwords.
* Build the image (first build is slow: it compiles CPython inside the image):

    ```shell
    docker compose build
    ```

* Test run the scripts with the default service. This runs `run_petl_dev.sh` for every group with sync **off** (matches Option A's behavior):

    ```shell
    docker compose up
    ```

The `compose.yml` also defines two opt-in services under Compose profiles:

* `dev` – same as the default, but bind-mounts your host `src/` on top of the image copy so code edits are picked up without rebuilding:

    ```shell
    docker compose run --rm dev
    ```

* `shell` – drops you into `bash` inside the pyenv + poetry environment. Useful for ad-hoc `poetry run petl ...` invocations or poking around:

    ```shell
    docker compose run --rm shell
    ```

Running a single group ad-hoc (equivalent to editing the `for g in ...` loop in `run_petl_dev.sh`):

```shell
docker compose run --rm shell -lc '
  export $(grep -v "^#" ./.env | xargs) && \
  poetry run petl --config ./src/patron_groups/config/petl.ini \
                  --group faculty-base \
                  --ldap_passwd "$PGRPS_LDAP_PASSWD" \
                  --grouper_passwd "$PGRPS_GROUPER_PASSWD" \
                  --sync_max "$PGRPS_SYNC_MAX" \
                  --debug'
```

Notes:
* `.env` is mounted as a *file* (not passed via `env_file:` / `--env-file`) so that `run_petl_dev.sh`'s `grep .env | xargs` parses quoted values correctly, the same way it does on a local host.
* The container is intended for **development**. Production still deploys via `run_petl_prod.sh` on `petl.library.arizona.edu` (see below) — the container isn't part of the production path.

### Production deployment

Production petl.library.arizona.edu will run the Patron Groups scripts daily with a cron job that hits the `run_petl_prod.sh` script (sync is live).

**Requirements**
* The user needs to SSH in to petl.library.arizona.edu.
* The user needs to have `sudo` access to run the installation as the `patrongroups` user.

**Directions**
* Run `sudo su patrongroups`
* Change directory into `/usr/local/ual-patron-groups/`
* Run `./build.sh`, enter "prod" at the prompt.
* To test that the build version updated, enter the Python console and enter the following code:

    ```shell
    >>> import patron_groups
    >>> help(patron_groups)
    ```

**Crontab explanation**

`0 2 * * *  . ./.profile && cd /usr/local/ual-patron-groups && ./run_petl_prod.sh`

Everyday at 2AM, the `patrongroups` user will source the `~/.profile` to load the pyenv environment, then changes directory to `/usr/local/ual-patron-groups` and runs the production sync script.
    
## Petl script usage

The `petl` script that serves as the command line wrapper for the petal Python package is located at `src/patron_groups/scripts/petl`. Several of the usage parameters are set in `run_petl_prod.sh` and `run_petl_dev.sh`, with variables set in the .env file. To run the script by itself, it can be invoked from the project root directory with `$ python src/patron_groups/scripts/petl`. The following are command params output by the `--help` param from the script:

    ```shell
    Command-line driver for patron group ETL jobs.

    optional arguments:
    -h, --help            show this help message and exit
    --config CONFIG       path to configuration file for this ETL run
    --group GROUP         name of patron group (a.k.a. section) in configuration
                        file for this ETL run
    --ldap_host LDAP_HOST
                        LDAP host
    --ldap_base_dn LDAP_BASE_DN
                        base DN for LDAP bind and query
    --ldap_user LDAP_USER
                        user name for LDAP login
    --ldap_passwd LDAP_PASSWD
                        password for LDAP login
    --ldap_query LDAP_QUERY
                        query string for LDAP search
    --grouper_host GROUPER_HOST
                        Grouper host
    --grouper_base_path GROUPER_BASE_PATH
                        base path for Grouper API
    --grouper_user GROUPER_USER
                        user name for Grouper login
    --grouper_passwd GROUPER_PASSWD
                        password for Grouper login
    --grouper_stem GROUPER_STEM
                        stem for Grouper query and update
    --grouper_group GROUPER_GROUP
                        group for Grouper query and update
    --batch_size BATCH_SIZE
                        synchronization batch size
    --batch_timeout BATCH_TIMEOUT
                        synchronization batch timeout in seconds
    --batch_delay BATCH_DELAY
                        delay between batches in seconds
    --sync                perform synchronization
    --sync_max SYNC_MAX   maximum membership delta to allow when synchronizing
    --debug               turn on debug logging
    --slack SLACK         redirect logging to Slack webhook
    ```
    
## Petal configuration

Package configuration is set in `src/patron_groups/config/petl.ini`. (While this is the default configuration for the `petl` script, it would be nice to someday be able to load appended override configs from outside the package!) It loads the configuration for each individual Grouper group and enumerates the global defaults for the script if not set in command line arguments. See the header of the `petl.ini` for details: 

```shell
#
# Configuration for the "petl" script.
#
# Parameters are loaded in the following order:
#
#   1. Global defaults.
#   2. Per-group configurations (will override #1).
#   3. Command-line parameters (will override #1 and #2).
#

#
# Global defaults for all groups.
#

[global]
ldap_host         = eds.iam.arizona.edu
ldap_base_dn      = dc=eds,dc=arizona,dc=edu
ldap_user         = ual-pgrps
ldap_passwd       = ***override***
grouper_host      = grouper.iam.arizona.edu
grouper_base_path = grouper-ws/servicesRest/json/v2_2_001/groups
grouper_user      = ual-pgrps
grouper_passwd    = ***override***
grouper_stem      = arizona.edu:dept:LBRY:pgrps
batch_size        = 100
batch_timeout     = 60
batch_delay       = 0
sync_max          = 1000

#
# Per-group configurations.
#
...
```

## Maintainers

UA Libraries, TeSS-Dev Team

[python]: https://www.python.org/
[ldap]: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol
[grouper]: https://www.internet2.edu/products-services/trust-identity/grouper/
[shibboleth]: https://shibboleth.net/
[alpine]: https://alpinelinux.org/
[crond]: https://en.wikipedia.org/wiki/Cron
[homebrew]: https://brew.sh/
[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv
[poetry]: https://python-poetry.org/
[uv]: https://docs.astral.sh/uv/
[semver]: http://semver.org
