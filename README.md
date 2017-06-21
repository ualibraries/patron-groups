# UAL Patron Groups

## Overview

This is a small, quick [Python][python] hack that synchronizes [LDAP][ldap] queries against UA's
Enterprise Directory Service ("EDS") into [Grouper][grouper] groups living in UA's central
Grouper service.  In the original use case, those group memberships then show up as 
"isMemberOf" attributes in the information returned from a successful [Shibboleth][shibboleth] 
authentication; vendors running Shib-aware services can then use the "isMemberOf" 
information to make authorization and access control decisions.

The general principle -- exposing the complexity of "who gets access to what" as simple
authorization attributes based on group membership -- should hopefully be broadly 
applicable to other use cases in the future.

## Setup

This software is implemented as a Python module that includes a primary library ("petal")
and a command-line driver script ("petl").  The simplest way to use it is to use something 
like [pyenv][pyenv] and [pyenv-virtualenv][pyenv-virtualenv] to create a Python interpreter
installation specific to the module, and then use "pip" to do a local (symlinked) install
of the module.

For instance, on macOS, assuming you've already got the [Homebrew][homebrew] package manager
installed, you might do something like the following:

    % brew update
    % brew install pyenv
    % brew install pyenv-virtualenv
	% pyenv install 3.6.1
    % pyenv virtualenv 3.6.1 ual-patron-groups
    
        [ add lines to shell startup scripts per pyenv/pyenv-virtualenv output ]
    
    % git clone https://github.com/ualibraries/patron-groups ual-patron-groups
    % cd ual-patron-groups
    % pyenv local ual-patron-groups
    % pip install -e .

At this point, you should be able to run "petl" commands out of the root directory
of the project.

## Usage

A patron groups run needs about a dozen different parameters to specify all of the
relevant LDAP, Grouper, and batch processing information. The "petl" script looks in
three places to resolve those parameters:

*   Global defaults from a specified configuration file;
*   Per-group parameters from a specific section within that configuration file
    (overrides globals);
*   Command-line parameters (overrides globals and per-group values).

In general, I recommend specifying everything except passwords in the configuration file.

A "petl" invocation then looks like:

    % export REQUESTS_CA_BUNDLE="/usr/local/etc/openssl/incommon_rsa_ca_bundle.pem"
    % ./scripts/petl --config config/petl.ini \
                     --section students \
                     --ldap_passwd *[password]* \
                     --grouper_passwd *[password]* \
                     --sync

(Note the setting of the "REQUESTS_CA_BUNDLE" environment variable: our campus Grouper
instance uses an SSL CA chain from InCommon that may not be installed on the host
running the script -- [downloading the bundle][certs] and pointing to it as shown will
resolve any "CERTIFICATE_VERIFY_FAILED" errors you see coming out of the script.)

The script (using the supporting library) will then query LDAP to determine the
current set of UAIDs that match the query; query Grouper to determine the current population
of the corresponding group; compare the results of the two queries and determine
drops and adds to synchronize them; and finally perform those modifications to the group
in batches (doing them all at once for a big group can run into timeout issues with
the Grouper server, which is a little slow).

The output from the run will look something like:

    2017-06-21 09:04:02,345 INFO starting run:
    2017-06-21 09:04:02,345 INFO     config = config/petl.ini
    2017-06-21 09:04:02,345 INFO     section = students
    2017-06-21 09:04:02,346 INFO     ldap_host = eds.arizona.edu
    2017-06-21 09:04:02,346 INFO     ldap_base_dn = dc=eds,dc=arizona,dc=edu
    2017-06-21 09:04:02,346 INFO     ldap_user = ual-pgrps
    2017-06-21 09:04:02,347 INFO     ldap_passwd = (set)
    2017-06-21 09:04:02,347 INFO     ldap_query = (eduPersonAffiliation=student)
    2017-06-21 09:04:02,347 INFO     grouper_host = grouper.arizona.edu
    2017-06-21 09:04:02,347 INFO     grouper_base_path = grouper-ws/servicesRest/json/v2_2_001/groups
    2017-06-21 09:04:02,347 INFO     grouper_user = ual-pgrps
    2017-06-21 09:04:02,347 INFO     grouper_passwd = (set)
    2017-06-21 09:04:02,347 INFO     grouper_stem = arizona.edu:dept:LBRY:pgrps
    2017-06-21 09:04:02,347 INFO     grouper_group = ual-students
    2017-06-21 09:04:02,347 INFO     batch_size = 1000
    2017-06-21 09:04:02,347 INFO     batch_timeout = 900
    2017-06-21 09:04:02,347 INFO     sync = True
    2017-06-21 09:04:02,348 INFO     debug = False
    2017-06-21 09:04:02,348 INFO executing ldap query and compiling members
    2017-06-21 09:05:10,436 INFO found 55849 entries via LDAP query
    2017-06-21 09:05:10,437 INFO executing grouper query and compiling members
    2017-06-21 09:08:01,060 INFO found 55651 entries via Grouper query
    2017-06-21 09:08:01,073 INFO ldap and grouper have 55582 members in common
    2017-06-21 09:08:01,087 INFO synchronization will drop 69 entries from grouper group
    2017-06-21 09:08:01,080 INFO synchronization will add 267 entries to grouper group
    2017-06-21 09:08:01,087 INFO synchronizing ...
    2017-06-21 09:08:01,087 INFO synchronizing ldap query results to ual-students
    2017-06-21 09:08:01,088 INFO batch size = 1000, batch timeout = 900 seconds
    2017-06-21 09:08:01,088 INFO processing drops:
    2017-06-21 09:08:37,587 INFO dropped batch 1, 69 entries, 36 seconds
    2017-06-21 09:08:37,587 INFO processing adds:
    2017-06-21 09:09:37,946 INFO added batch 1, 267 entries, 60 seconds
    2017-06-21 09:09:37,946 INFO run complete.

You can leave off the "--sync" switch to do a dry run ("petl" will run the queries
and calculate the changes, but not actually execute them).  You can also add a "--debug"
switch to get additional trace logging as the process executes.

## Versioning

A few simple recommendations on [semantic versioning][semver]:

*   If you touch anything in the "petal" library code that then requires client-side changes in
    the "petl" script (e.g. you changed the library API), that's a major number change for 
    sure (1 → 2).
*   If you change things in the "petl" script, or add a new section to configuration in "petl.ini",
    that's probably a minor version increment (1.1 → 1.2).
*   If you're making a small tweak to an existing configuration, or fixing a minor bug that doesn't
    otherwise change the library or command-line API, that's a patch increment (1.5.2 → 1.5.3).
    
As always, these are just suggestions.

## Maintainers

Mike Simpson, mgsimpson@email.arizona.edu


[python]: https://www.python.org/
[ldap]: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol
[grouper]: https://www.internet2.edu/products-services/trust-identity/grouper/
[shibboleth]: https://shibboleth.net/
[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv
[homebrew]: https://brew.sh/
[certs]: https://spaces.internet2.edu/display/ICCS/InCommon+Cert+Types
[semver]: http://semver.org/
