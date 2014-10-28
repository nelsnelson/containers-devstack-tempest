#! /usr/bin/env bash

[[ -z `cat /etc/timezone | grep "America/Chicago"` ]] && (echo "America/Chicago" | tee /etc/timezone)
cat /etc/timezone
dpkg-reconfigure --frontend noninteractive tzdata
apt-get install --fix-missing --assume-yes ntpdate
ntpdate pool.ntp.org

