#!/bin/sh
set -e

PREFIX=${PREFIX:-/opt/m3u8downloader}
LOGDIR=${LOGDIR:-/var/log/m3u8downloader}
RUN_AS_USER=www-data

mkdir -p "$LOGDIR"
# touch /var/log/m3u8downloader/uwsgi.touch
if [ "$RUN_AS_USER" != root ]; then
	chown -R "$RUN_AS_USER":"$RUN_AS_USER" "$LOGDIR"
fi

cd "$PREFIX"
make bootstrap
# make install

# install crontab, systemd service, nginx site file, logrotate config etc

# if you enable logrotate.conf, remember to choose a good rotate interval and
# set how many copies to keep.

# install -m 644 "$PREFIX/conf/logrotate.conf" /etc/logrotate.d/m3u8downloader
# install -m 644 "$PREFIX/conf/web.upstart" /etc/init/m3u8downloader.conf
# install -m 644 "$PREFIX/conf/web.service" /etc/systemd/system/m3u8downloader.service
# service m3u8downloader start || true

# SITE_FILE=/etc/nginx/conf.d/m3u8downloader.conf
# if [ -e "$SITE_FILE" ]; then
# 	echo "warning: not overwriting existing nginx site file $SITE_FILE"
# else
# 	install "$PREFIX/conf/http.site" "$SITE_FILE"
# 	service nginx reload
# fi
