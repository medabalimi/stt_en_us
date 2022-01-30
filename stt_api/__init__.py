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

from flask import Flask
from flask_ipban import IpBan

from stt_api.celerifier import make_celery
import requests



import os
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)

app.config.from_object('config')
app_path='/'.join(app.root_path.split('/')[:-1])

app.config['MOUNT_POINT'] = f"{app_path}/mount"
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


app.config['UPLOAD_FOLDER'] = f"{app.config['MOUNT_POINT']}/{app.config['RELATIVE_UPLOAD_FOLDER']}"
app.config['REDACTED_FOLDER'] = f"{app.config['MOUNT_POINT']}/{app.config['RELATIVE_REDACTED_FOLDER']}"

app.config['DB_FOLDER'] = f"{app.config['MOUNT_POINT']}/database"
app.config['ASR_MODEL_FOLDER'] = f"{app_path}/models/asr"
app.config['TMP_FOLDER'] = f"{app.config['MOUNT_POINT']}/tmp"
app.config['TASK_LOG_FILE'] = f"{app.config['DB_FOLDER']}/task_list.txt"

dir_list = ['UPLOAD_FOLDER', 'REDACTED_FOLDER', 'DB_FOLDER', 'ASR_MODEL_FOLDER', 'TMP_FOLDER']

app.config['JSON_AS_ASCII'] = False

for d in dir_list:
    if not os.path.isdir(app.config[d]):
        os.makedirs(app.config[d], exist_ok=True)

if not os.path.isdir(app.config['REDACTED_FOLDER']):
    os.makedirs(app.config['REDACTED_FOLDER'], exist_ok=True)

app.config['IP_BAN_LIST_COUNT'] = 6
app.config['IP_BAN_LIST_SECONDS'] = 3600

ip_ban = IpBan(app)
ip_ban.load_nuisances()
celery_tasks = make_celery(app)

import stt_api.routes
