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


import collections

import sys

import webrtcvad

import numpy as np

# CONFIG
frame_size = 30
vad_sensitivity = 2


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


'''
Get VAD boundaries. Returns an iterator
'''


def get_vad(sample_rate, frame_duration_ms,
            padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    for frame in frames:
        # sys.stdout.write('1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                #       sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                seg_start = ring_buffer[0].timestamp
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                #        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                seg_end = frame.timestamp + frame.duration
                triggered = False
                yield (seg_start, seg_end)
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
        seg_end = frame.timestamp + frame.duration
    # sys.stdout.write('\n')
    if voiced_frames:
        yield (seg_start, seg_end)


'''
Convert numpy float to 16bit pcm (byte stream)
'''

def convert_np_to_pcm(audio):
    for ch, signal in enumerate(audio.T):
        pcm_data = np.int16(signal * 32768 / max(abs(signal))).tobytes()
        yield (pcm_data, ch)


def get_segments(audio, fs):
    silence = 0
    speech = 0
    for (signal, channel) in convert_np_to_pcm(audio):
        vad = webrtcvad.Vad(vad_sensitivity)
        print("Processing channel #", channel)
        frames = frame_generator(frame_size, signal, fs)
        frames = list(frames)
        prev_segend = 0

        boundaries = get_vad(fs, frame_size, 300, vad, frames)
        for (segstart, segend) in boundaries:
            segstart = max(prev_segend, segstart - 2 * frame_size / 1000)
            segend = segend + 2 * frame_size / 1000;
            if segstart - prev_segend > 0.5:
                silence += segstart - prev_segend
            speech += segend - segstart
            prev_segend = segend
            yield (channel, float(format(segstart, '.3f')), float(format(segend, '.3f')), float(format(speech, '.3f')))


if __name__ == '__main__':
    import soundfile as sf
    args=sys.argv[1:]

    if len(args) < 2:
        sys.stderr.write(
            'Usage: example.py <vad sensitivity> <path to wav file> <channel>\n')
        sys.exit(1)

    wavfile = args[1]
    vad_sensitivity = int(args[0])

    channels = sf.info(wavfile).channels
    audio, sample_rate = sf.read(wavfile)

    segbounds = get_segments(audio, sample_rate, channels)
    for (ch, segstart, segend, speech) in segbounds:
        print(ch, segstart, segend)

    print('total speech  = ', speech)
    print('total silence = ', sf.info(args[1]).duration - speech)
