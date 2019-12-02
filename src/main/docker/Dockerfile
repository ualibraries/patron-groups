FROM alpine:3.10.3

ENV PACKAGES="dumb-init bash python3 python3-dev ca-certificates tzdata" \
    LDAP_PASSWD="***supply at runtime***" \
    GROUPER_PASSWD="***supply at runtime***" \
    SLACK_WEBHOOK="***supply at runtime***"

ADD petal-1.5.1.tar.gz /var/tmp
ADD run_petl /etc/periodic/daily

RUN echo \
  #
  # set installed script as executable
  && chmod +x /etc/periodic/daily/run_petl \
  #
  # add packages
  && apk add --no-cache $PACKAGES \
  #
  # add symlinks
  && if [[ ! -e /usr/bin/python ]];        then ln -sf /usr/bin/python3 /usr/bin/python; fi \
  && if [[ ! -e /usr/bin/python-config ]]; then ln -sf /usr/bin/python3-config /usr/bin/python-config; fi \
  && if [[ ! -e /usr/bin/pydoc ]];         then ln -sf /usr/bin/pydoc3 /usr/bin/pydoc; fi \
  && if [[ ! -e /usr/bin/pip ]];           then ln -sf /usr/bin/pip3 /usr/bin/pip; fi \
  #
  # set timezone
  && cp /usr/share/zoneinfo/US/Arizona /etc/localtime \
  && echo "US/Arizona" >  /etc/timezone \
  #
  # install petal
  && pip install --trusted-host pypi.python.org -r /var/tmp/petal-1.5.1/requirements.txt \
  && pip install /var/tmp/petal-1.5.1

ENTRYPOINT [ "/usr/bin/dumb-init", "--" ]
CMD [ "/usr/sbin/crond", "-f" ]
