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
import os
from stt_api import celery_tasks

from celery.exceptions import Ignore

import nemo.collections.asr as nemo_asr

import soundfile as sf

import tempfile

from speech import fastvad
from speech.audio import read_file
import torch
import ffmpeg

import numpy as np


def generate_segments(audio, sample_rate, temp_dir):
    """
    :param audio:
    :param sample_rate:
    :param temp_dir:
    :return:
    """
    segbounds = fastvad.get_segments(audio, sample_rate)
    segments = {}
    files_list = []
    for (ch, segstart, segend, speech) in segbounds:
        temp_segment_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.wav')
        segments[temp_segment_file.name] = {'channel': ch, 'start': segstart, 'end': segend}
        files_list.append(temp_segment_file.name)
        start_sample = np.floor(sample_rate * segstart).astype(int)
        end_sample = np.ceil(sample_rate * segend).astype(int)

        sf.write(temp_segment_file.name, audio[start_sample:end_sample, ch].astype('int16'), sample_rate,
                 subtype='PCM_16')
    return segments, files_list


@celery_tasks.task(bind=True)
def recognize_speech(self, audio_file, model_file, tmp_dir='/tmp'):
    task_id = recognize_speech.request.id
    print(f"Processing {audio_file} using {model_file}")
    try:

        meta_content = {'id': task_id,
                        'stage': 'Initializing',
                        'message': 'Reading audio file'}

        #meta_content['fileinfo']  = ffmpeg.probe(audio_file)
        #meta_content['model']=model_file.split('/')[-1].split('.')[0]


        self.update_state(state='PROCESSING',
                          meta=meta_content)



        audio, sample_rate, channels = read_file(audio_file, target_sample_rate=16000)

        with tempfile.TemporaryDirectory(dir=tmp_dir) as temp_dir:

            meta_content['stage'] = 'VAD'
            meta_content['message'] = 'Generating voice segments'
            segments, files_list = generate_segments(audio, sample_rate, temp_dir)

            self.update_state(state='PROCESSING',
                              meta=meta_content)

            meta_content['stage'] = 'ASR'
            meta_content['message'] = 'Loading model'

            asr_model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(restore_path=model_file)
            meta_content['message'] = 'Converting speech to text'
            self.update_state(state='PROCESSING',
                              meta=meta_content)

            torch.set_num_threads(os.cpu_count() - 1)
            with torch.no_grad():
                transcriptions = asr_model.transcribe(paths2audio_files=files_list)[0]

            asr_out = []
            for (text, file_name) in zip(transcriptions, files_list):
                segments[file_name]['text'] = text
                asr_out.append(segments[file_name])






    except Exception as exp:
        meta_content['exception'] = str(exp)
        self.update_state(state='FAILED',
                          meta=meta_content)

        os.remove(audio_file)

        raise Ignore()
    else:
        os.remove(audio_file)

        meta_content['transcript'] = asr_out
        return meta_content
