# -*- coding: utf-8 -*-

import os
import numpy as np
import scipy
import scikits.audiolab as audiolab
from random import random, randint

get_path = lambda x, y: "Redo/Individual/{}/{}.wav".format(x, y)
silence, _, _ = audiolab.wavread('Redo/Individual/Silence/0.wav')
freq = 16000
encode = "pcm16"

def get_silence(base_time=0.00, max_time=0.025):
    global silence
    quiet_time = (max_time - base_time)*random() + base_time
    max_silence = float(len(silence))/float(freq) # in seconds
    start_idx = randint(0, int((max_silence - quiet_time)*freq))
    end_idx = start_idx + int(quiet_time*freq)
    return silence[start_idx: end_idx]

def smooth(sound, lamb=0.1):
    amt = int(lamb*float(len(sound)))
    for i in range(amt):
        sound[i] = i/amt*sound[i]
        sound[len(sound) - i - 1] = i/amt*sound[len(sound) - i - 1]
    return sound

def unsmooth(sound, coeff=1.25, lamb=0.1):
    amt = int(lamb*float(len(sound)))
    for i in range(amt):
        sound[i] = (coeff - i/amt)*sound[i]
        sound[len(sound) - i - 1] = (coeff - i/amt)*sound[len(sound) - i - 1]
    return sound

def trim(sound, front=0.05, back=0.15):
    startIdx = int(front*float(len(sound)))
    endIdx = len(sound) - int(back*float(len(sound)))
    return sound[startIdx:endIdx]

def get_file(category, is_cut=True):
    fileIdx = randint(0, 5)
    path = get_path(category, fileIdx)
    if is_cut:
        return unsmooth(trim(audiolab.wavread(path)[0], front=0.1))
    return audiolab.wavread(path)[0]

def blend(sounds, blend=0.5, fs=16000):
    # Linear blend
    sound = []
    prevEnd = 0
    nextStart = 0
    avg = []
    for idx, s in enumerate(sounds):
        if idx == 0:
            prevEnd = len(s) - int(blend*float(freq))
            sound.append(s[:prevEnd])
            avg = s[prevEnd:].copy()
        elif idx == len(sounds) - 1:
            # Add blend
            nextStart = int(blend*float(freq))
            for i in range(min(len(avg), len(s))):
                avg[i] = (avg[i] + s[i])/2
            sound.append(avg[:])
            sound.append(s[min(len(avg), len(s)):])
        else:
            # Add blend
            nextStart = int(blend*float(freq))
            for i in range(min(len(avg), len(s))):
                avg[i] = (avg[i] + s[i])/2
            sound.append(avg[:])
            # Reset value
            prevEnd = len(s) - int(blend*float(freq))
            sound.append(s[:prevEnd])
            avg = s[prevEnd:]
    
    return scipy.concatenate(tuple(sound))

def get_sound_attatch(cat1, num1, cat2, num2):
    return scipy.concatenate((
        get_silence(0, 0.1),
        get_file(cat1),
        get_silence(),
        get_file(num1),
        get_silence(),
        get_file("Pai"),
        get_silence(),
        get_file(cat2),
        get_silence(),
        get_file(num2),
        get_silence(0, 0.1)
    ))

def get_sound_blend(cat1, num1, cat2, num2):
    # Create sequence
    # Need to fine tuned sound per person
    # As each person bias is not equal
    return blend([
        get_silence(0, 0.1),
        get_file(cat1),
        get_silence(),
        get_file(num1),
        get_silence(),
        get_file("Pai"),
        get_silence(),
        get_file(cat2),
        get_silence(),
        get_file(num2),
        get_silence(0, 0.1)
    ])

# Choose blend mode
# get_sound = get_sound_attatch
get_sound = get_sound_blend

base_file = "transcript_idx_eng.txt"
get_out_path = lambda x: "Redo/Merge/{}.wav".format(x)
total_length = 0
with open(base_file, "r") as file:
    for line in file:
        if len(line.strip()) == 0:
            continue
        file_name, cat1, num1, _, cat2, num2 =line.strip().split(" ")
        sound = get_sound(cat1, num1, cat2, num2)
        total_length += len(sound) 
        audiolab.wavwrite(sound, get_out_path(file_name), freq, encode)
print("Done! with total sound of {:.3f} seconds".format(float(total_length)/float(freq)))

"""
File Structure
--------------
merge.py
transcript_idx_eng.txt
Redo/
├── Individual
│   ├── 1
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── 2
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── 3
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── 4
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── B
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── C
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── D
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── E
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── F
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── G
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   ├── Pai
│   │   ├── 0.wav
│   │   ├── 1.wav
│   │   ├── 2.wav
│   │   ├── 3.wav
│   │   ├── 4.wav
│   │   └── 5.wav
│   └── Silence
│       └── 0.wav
└── Merge
"""