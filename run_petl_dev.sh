#!/bin/bash

# dev version of run script omits sync (important for testing) and slack (no one wants to know)

export $(grep -v '^#' ./.env | xargs) # get env args mentioned below

for g in faculty-base staff-base students-base ugrads-base grads-base dcc-base retirees-base hsl-base law-base
do
    ./src/main/python/scripts/petl --config ./src/main/python/config/petl.ini \
                  --group ${g} \
                  --ldap_passwd ${PGRPS_LDAP_PASSWD} \
                  --grouper_passwd ${PGRPS_GROUPER_PASSWD}
done

