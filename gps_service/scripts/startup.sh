#!/bin/sh

if [ -f /data/.env ]
then
	source /data/.env
fi

start_app() {
	cd /usr/share/gpsserviceapp
	python3 gps_service.py
}

_term() {
  echo "Caught SIGTERM signal!"
  kill -TERM "$pid" 2>/dev/null
}                              
                               
trap _term SIGTERM

case "$1" in
start)
        echo -n "Starting GPS service\n"
        start_app
        echo "done."
        ;;

stop)
        echo -n "Stopping GPS service"
        pidof python3 | xargs kill -15
        : exit 0
        echo "done."
        ;;

# force-reload|restart)
#         echo "Reconfiguring phapp"
#         echo "done."
#         ;;

*)
        echo "Usage: /usr/share/gpsserviceapp {start|stop}"
        exit 1
        ;;
esac

exit 0
