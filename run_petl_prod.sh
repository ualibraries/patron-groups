#!/bin/bash

export $(grep -v '^#' ./.env | xargs)

for g in faculty-base staff-base students-base ugrads-base grads-base dcc-base retirees-base hsl-base law-base library-employees-base
do
    ./src/main/python/scripts/petl --config ./src/main/python/config/petl.ini \
                  --group ${g} \
                  --ldap_passwd ${PGRPS_LDAP_PASSWD} \
                  --grouper_passwd ${PGRPS_GROUPER_PASSWD} \
                  --slack ${PGRPS_SLACK_WEBHOOK} \
                  --slack_ping_users ${SLACK_PING_USERS} \
                  --sync_max ${PGRPS_SYNC_MAX} \
                  --sync
done
