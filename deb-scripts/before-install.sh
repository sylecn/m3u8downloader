#!/bin/sh
set -e

stop_upstart_service_maybe() {
	service="$1"
	if [ -e /etc/init/${service}.conf ]; then
		if status "$service" |grep 'start/running'; then
			stop "$service" || true
		fi
	fi
}
stop_systemd_service_maybe() {
	service="$1"
	if [ -e /etc/systemd/system/${service}.service ]; then
		if systemctl -q is-active "$service"; then
			systemctl stop "$service" || true
		fi
	fi
}

cd /
# stop_systemd_service_maybe m3u8downloader
