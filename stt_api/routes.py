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

from flask import request, redirect, jsonify, flash, url_for, Response, abort, send_from_directory
from werkzeug.utils import secure_filename
import ffmpeg
import json
from stt_api import app
from stt_api import celery_tasks
import uuid
import os
import time
from tasks.stt_task import recognize_speech


def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_asr_model(model_type):
    asr_model = app.config['ASR_MODELS'].get(model_type, 'best')

    return f"{app.config['ASR_MODEL_FOLDER']}/{asr_model}.nemo"


@app.route('/tasks')
def get_tasks():
    """ Endpoint that returns the uuids of the tasks submitted
        ---
       summary: Returns the valid list of task ids for files submitted
       responses:
        '200':
          description: Response tracking the status of submitted STT job
          content:
            application/json:
        '400':
          description: Invalid or missing file.

        """
    try:
        with open(app.config['TASK_LOG_FILE'], 'r') as ifp:
            list_of_taskids = [f.strip() for f in ifp]
    except Exception as exp:
        list_of_taskids = []
    task_status = {}
    for task_id in list_of_taskids:
        task_status[task_id] = {'status': recognize_speech.AsyncResult(task_id).state,
                                'url': f"http://{request.host}{url_for('taskstatus', task_id=task_id)}"}
    return jsonify(task_status)


@app.route('/status/<task_id>')
def taskstatus(task_id):
    """ Get status of task specified by {task_id}
    Endpoint that returns the status of a task specified by {task_id}. {task_id} is obtained when a STT job is submitted in /stt/{model_type}.
    Please note that even invalid values for {task_id} will return PENDING state. Check '/tasks' endpoint for actual list of tasks

        ---
       summary: Returns the status of a task specified by {task_id}
       parameters:
         - name: task_id
           in: path
           type: string
           format: uuid
           required: true
       responses:
        '200':
          description: Response tracking the status of submitted STT job.
          content:
            application/json:
        '400':
          description: Invalid or missing file.

        """
    task = recognize_speech.AsyncResult(task_id)

    if task.state == 'PENDING':
        # job did not start yet
        task_real_state = 'INVALID'
        with open(app.config['TASK_LOG_FILE'], 'r') as ifp:
            list_of_taskids = [f.strip() for f in ifp]
        if task_id in list_of_taskids:
            task_real_state=task.state
        response = {
            'state': task_real_state,
            'status': task.info
        }
    elif (task.state == 'PROGRESS') or (task.state == 'SUCCESS'):
        response = {
            'state': task.state,
            'status': task.info
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': str(task.state),
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

#@app.route('/stt/', defaults={'model_type': 'best'}, methods=['POST'])
@app.route('/stt/<model_type>', methods=['POST'])
def stt(model_type='best'):
    """ Submits STT jobs asynchronously. Additional jobs are queued and processed sequentially.
    Asynchronous Endpoint that takes an audio file as input along with the type of asr model (['best', 'good', 'fast']) to be used.
    Returns a JSON containing the URL  ('task_url') where the result will be available
        ---
       summary: Uploads aan audio file and convert speech to text. This
       consumes:
         - multipart/form-data
       parameters:
         - name: model_type
           in: path
           type: string
           enum: ['best', 'good', 'fast']
           required: false
           default: best
         - in: formData
           name: file
           type: file
           required: true
           description: The audio file to upload.
       responses:
        '200':
          description: Response tracking the status of submitted STT job
          content:
            application/json:
        '400':
          description: Invalid or missing file.

        """

    if request.method == 'POST':
        print(request.files)
        if ('file' not in request.files) and ('data' not in request.files):
            return abort(400, "Missing audio file in POST request")

        if ('file' in request.files):
            file = request.files['file']
        else:
            file = request.files['data']

        try:
            if file and allowed_files(file.filename):
                filename = f'{uuid.uuid4()}_{secure_filename(file.filename)}'
                audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(audio_file_path)

                fileinfo = ffmpeg.probe(audio_file_path)
                asr_model = get_asr_model(model_type)
                asr_output = recognize_speech.delay(audio_file_path, asr_model, app.config['TMP_FOLDER'])
                fileinfo['task_url'] = f"http://{request.host}{url_for('taskstatus', task_id=asr_output.id)}"
                with open(app.config['TASK_LOG_FILE'], 'a+') as ifp:
                    ifp.write(asr_output.id + '\n')

                time.sleep(2)
                return jsonify(fileinfo)
            else:
                return abort(400, "Invalid file type. Not a media/audio file")

        except Exception as exp:
            print(exp)
            return abort(500, str(exp))
    else:
        return redirect('/apidocs')
