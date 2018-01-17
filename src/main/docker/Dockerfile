FROM alpine:3.6

ENV PACKAGES="dumb-init musl bash python3 python3-dev ca-certificates tzdata" \
	REQUESTS_CA_BUNDLE="/etc/petal/incommon_rsa_ca_bundle.pem" \
	LDAP_PASSWD="***supply at runtime***" \
	GROUPER_PASSWD="***supply at runtime***" \
	SLACK_WEBHOOK="***supply at runtime***"

ADD petal-1.2.4.tar.gz /var/tmp
ADD run_petl /etc/periodic/daily

RUN echo \

  # set installed script as executable
  && chmod +x /etc/periodic/daily/run_petl \

  # add edge repositories
  && echo "@edge-testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
  && echo "@edge-community http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
  && echo "@edge-main http://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories \

  # add packages
  && apk add --no-cache $PACKAGES \

  # add symlinks
  && if [[ ! -e /usr/bin/python ]];        then ln -sf /usr/bin/python3 /usr/bin/python; fi \
  && if [[ ! -e /usr/bin/python-config ]]; then ln -sf /usr/bin/python3-config /usr/bin/python-config; fi \
  && if [[ ! -e /usr/bin/idle ]];          then ln -sf /usr/bin/idle3 /usr/bin/idle; fi \
  && if [[ ! -e /usr/bin/pydoc ]];         then ln -sf /usr/bin/pydoc3 /usr/bin/pydoc; fi \
  && if [[ ! -e /usr/bin/pip ]];           then ln -sf /usr/bin/pip3 /usr/bin/pip; fi \
  
  # set timezone
  && cp /usr/share/zoneinfo/US/Arizona /etc/localtime \
  && echo "US/Arizona" >  /etc/timezone \
  
  # install petal
  && pip install --trusted-host pypi.python.org -r /var/tmp/petal-1.2.4/requirements.txt \
  && pip install /var/tmp/petal-1.2.4

ENTRYPOINT [ "/usr/bin/dumb-init", "--" ]
CMD [ "/usr/sbin/crond", "-f" ]
