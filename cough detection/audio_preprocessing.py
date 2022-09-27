# -*- coding: utf-8 -*-

import os

"""1. mp3 파일을 wav로 변환"""

file_path = './non_data_mp3/'

from pydub import AudioSegment

def convert_wav(FILENAME):
    file_wav = FILENAME[:-4] +".wav"
    path = file_path + FILENAME
    
    sound = AudioSegment.from_mp3(path) 
    sound.export(file_wav, format="wav")
    #os.remove(file_mp3)

# Commented out IPython magic to ensure Python compatibility.
files = os.listdir(file_path)
# %cd '/content/drive/MyDrive/non_data/'

for file in files:
  convert_wav(file)

"""2. 음성 길이 맞추기 (5초)"""

"""2-1 5초로 맞추기 (Crop & Padding)"""

from pydub import AudioSegment
empty = AudioSegment.from_wav('/content/drive/MyDrive/empty.wav')  # 무음 파일 로드

def pad_wav(filename):
  path = file_path + filename
  sound = AudioSegment.from_wav(path)
  filename_o = filename[:-4]

  five_seconds = 5 * 1000

  if len(sound) == five_seconds:
    sound.export('{}_5.wav'.format(filename_o), format="wav")

  elif len(sound) < five_seconds:
    while len(sound) <= 5000:     # 5초가 넘을 때까지 padding
      sound = sound.append(empty)

    sound = sound[0:five_seconds]
    sound.export('{}_p.wav'.format(filename_o), format="wav")   # padding 표시

  elif len(sound) > five_seconds:
    sound_5sec = sound[0:five_seconds]
    sound_5sec.export('{}_c.wav'.format(filename_o), format="wav")  # cropping 표시

import os
file_path = './train/'
file_list = os.listdir(file_path)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/5_sec

cnt = 0
for file in file_list:
  try:
    pad_wav(file)
    cnt += 1
    print(file,' done ',cnt) # 완료한 파일 개수 확인
  except:
    continue

len(os.listdir('/content/drive/MyDrive/5_sec'))

"""2-2 5초 단위로 자르기"""

from pydub import AudioSegment
import math

def cut_wav(filename):
  path = file_path + filename
  sound = AudioSegment.from_wav(path)
  filename_o = filename[:-4]

  five_seconds = 5 * 1000

  for i in range(int(math.floor(len(sound)/5000))):
    print(filename)
    print(i)
    slice = sound[i*five_seconds:five_seconds*(i+1)]
    slice.export('{}_{}.wav'.format(filename_o,i), format="wav")

# Commented out IPython magic to ensure Python compatibility.
file_path = '/content/drive/MyDrive/project_cough/project-sesac-main/data/20220810/1.Training/non_cough/'
files = os.listdir(file_path)
# %cd '/content/drive/MyDrive/dataset/non_5sec/'

for file in files:
  cut_wav(file)