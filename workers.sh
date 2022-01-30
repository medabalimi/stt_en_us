#!/bin/bash

./check_deps.sh || exit 1
LOG_DIR=mount/logs

exec celery  -A stt_api.celery_tasks worker -P solo --max-tasks-per-child 1 -f $LOG_DIR/celery.log -n stt_worker1.%h

