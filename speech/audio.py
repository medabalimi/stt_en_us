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

import librosa

def read_file(audio_file, target_sample_rate=None):
    signal, fs = librosa.load(audio_file, mono=False, sr=None)
    if target_sample_rate is not None:
        if target_sample_rate != fs:
            signal=librosa.resample(signal,fs,target_sample_rate)
    fs=target_sample_rate
    if signal.ndim == 1:
        signal = signal.reshape(signal.shape[0], -1)
    elif signal.shape[1] > signal.shape[0]:
        signal = signal.T


    if signal.max() <= 32767 / 2:
        signal = signal * 32767 / signal.max()
    [length, channels] = signal.shape

    return signal, fs, channels
