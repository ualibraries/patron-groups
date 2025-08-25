#!/bin/bash

# dev version of run script omits sync (important for testing) and slack (no one wants to know)

export $(grep -v '^#' ./.env | xargs) # get env args mentioned below

for g in faculty-base staff-base students-base ugrads-base grads-base dcc-base retirees-base finearts-base hsl-base law-base library-employees-base emeritus-base
do
    poetry run petl --config ./src/patron_groups/config/petl.ini \
                  --group ${g} \
                  --ldap_passwd ${PGRPS_LDAP_PASSWD} \
                  --grouper_passwd ${PGRPS_GROUPER_PASSWD} \
                  --sync_max ${PGRPS_SYNC_MAX} \
                  --debug
done
