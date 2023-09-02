#! /usr/bin/env sh

echo "Starting cron job"

if pgrep -x "run_cron_job.sh" > /dev/null ; then
    echo "Cron job already running, aborting"
    exit 0
fi

STATIC_PATH=/etc/data/static EVENTS_DB_PATH=/etc/data/events_database.db /usr/local/bin/python /usr/src/app/convert_stories_to_text.py
