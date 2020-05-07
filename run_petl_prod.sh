#!/bin/bash

export $(grep -v '^#' .env | xargs)

for g in faculty-base staff-base students-base ugrads-base grads-base dcc-base retirees-base hsl-base law-base
do
    ./src/main/python/petl --config ./src/main/python/config/petl.ini \
                  --group ${g} \
                  --ldap_passwd ${PGRPS_LDAP_PASSWD} \
                  --grouper_passwd ${PGRPS_GROUPER_PASSWD} \
                  --sync
done
