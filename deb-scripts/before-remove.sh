#!/bin/sh
set -e

PREFIX=${PREFIX:-/opt/m3u8downloader}

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

# delete installed cron jobs, systemd service files, and binaries.
# rm -f /etc/logrotate.d/m3u8downloader
# rm -f /etc/init/m3u8downloader.conf
# rm -f /etc/systemd/system/m3u8downloader.service
# echo "You can safely delete /etc/nginx/conf.d/m3u8downloader.conf if it's no longer needed"

if [ -d "$PREFIX" ]; then
	make -C "$PREFIX" full-clean
fi
