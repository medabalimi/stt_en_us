"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#  http://www.apache.org/licenses/LICENSE-2.0

# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

"""

import socket
import os

CELERY_BROKER_URL = 'amqp://localhost:5672'
CELERY_RESULT_BACKEND = 'db+sqlite:///mount/database/results.db'

APPLICATION_NAME = 'stt'
CELERY_DEFAULT_EXCHANGE_NAME = '{}_exchange'.format(APPLICATION_NAME)
CELERY_DEFAULT_QUEUE_NAME = '{}_queue'.format(APPLICATION_NAME)
CELERY_TASK_TRACK_STARTED = True



task_queues = {f"{CELERY_DEFAULT_QUEUE_NAME}": {"exchange": f"{CELERY_DEFAULT_EXCHANGE_NAME}",
                                                  "binding_key": f"{CELERY_DEFAULT_QUEUE_NAME}"}}

task_default_queue = f"{CELERY_DEFAULT_QUEUE_NAME}"

ASR_MODELS = {'best': 'stt_en_contextnet_1024',
              'good': 'stt_en_contextnet_512',
              'fast': 'stt_en_contextnet_256' }

RELATIVE_UPLOAD_FOLDER = 'uploads'
RELATIVE_REDACTED_FOLDER = 'redacted'

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'opus', 'm4a', 'mp4', 'mkv'])

ASR_EXCHANGE = 'stt'
ASR_EXCHANGE_TYPE = 'topic'
ASR_STAGE_ONE = 'stt.segment'
ASR_STAGE_TWO = 'stt.recognize'
ASR_JOB_ROUTING_KEY = 'stt.job'
ASR_OP_ROUTING_KEY = 'stt.output.{}'
ASR_ERROR_ROUTING_KEY = 'stt.error.{}'
ASR_STATUS = 'stt.status.{}'
