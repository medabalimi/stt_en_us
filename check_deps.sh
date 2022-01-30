#!/bin/bash
MODEL_DIR=mount/models/asr/
DB_DIR=mount/database
LOG_DIR=mount/logs

[[ -d $MODEL_DIR ]] || mkdir $MODEL_DIR

[[ -d $DB_DIR ]] || mkdir -p $DB_DIR
[[ -d $LOG_DIR ]] || mkdir -p mount/logs

exit 0
