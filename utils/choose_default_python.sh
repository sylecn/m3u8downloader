#!/bin/sh
set -e

print_help_and_exit() {
	echo "Usage: choose_default_python.sh
choose a default python command for creating virtualenv.

Current preferences is:
python in /home dir > /opt dir > /usr dir
prefer python3 over python2.7,
"
	exit 1
}

# main()
if [ "$1" = "--help" ]; then
	print_help_and_exit
fi

first_existing_file()
{
	for f in "$@"
	do
		if [ -e "$f" ]; then
			re="$f"
			return 0
		fi
	done
	re=""
	return 1
}

# main()
if first_existing_file \
        ~/bin/python3 \
        ~/opt/bin/python3 \
	/usr/local/bin/python3 \
        /usr/bin/python3 \
	/usr/bin/local/python3 \
        /usr/bin/python; then
	echo "$re"
else
	echo "Error: failed to locate python" > /dev/stderr
fi
