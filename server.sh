#!/bin/bash
./check_deps.sh || exit 1
python3 download_models.py
LOG_DIR=mount/logs
#python3 download_models.py
exec gunicorn -w 4 --bind 0.0.0.0:5000 --log-file $LOG_DIR/gunicorn.log wsgi:app

