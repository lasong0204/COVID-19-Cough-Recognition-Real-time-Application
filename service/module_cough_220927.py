import pyaudio
import wave
import datetime

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd

import torch
import torch.nn as nn
import os

import torchvision.transforms as T
from PIL import Image 



# 파일 삭제 함수
def del_file(OUTPUT_FILENAME):
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
    MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"

    os.remove(WAVE_OUTPUT_FILENAME)
    os.remove(MFCC_OUTPUT_FILENAME)
    os.remove(MELS_OUTPUT_FILENAME)

    print("--------------------------")
    print("Del "+ WAVE_OUTPUT_FILENAME)
    print("Del "+ MFCC_OUTPUT_FILENAME)
    print("Del "+ MELS_OUTPUT_FILENAME)
    print("--------------------------")



# 파일 이름변경 함수
def rename_file(OUTPUT_FILENAME, CLASS_NAME):
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
    MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"

    WAVE_OUTPUT_FILENAME_RE = OUTPUT_FILENAME +"_"+ str(CLASS_NAME) +".wav"
    MFCC_OUTPUT_FILENAME_RE = OUTPUT_FILENAME +"_"+ str(CLASS_NAME) +".csv"
    MELS_OUTPUT_FILENAME_RE = OUTPUT_FILENAME +"_"+ str(CLASS_NAME) +".png"

    os.rename(WAVE_OUTPUT_FILENAME, WAVE_OUTPUT_FILENAME_RE)
    os.rename(MFCC_OUTPUT_FILENAME, MFCC_OUTPUT_FILENAME_RE)
    os.rename(MELS_OUTPUT_FILENAME, MELS_OUTPUT_FILENAME_RE)
    print("--------------------------")
    print("Rename "+ WAVE_OUTPUT_FILENAME_RE)
    print("Rename "+ MFCC_OUTPUT_FILENAME_RE)
    print("Rename "+ MELS_OUTPUT_FILENAME_RE)
    print("--------------------------")



# 각 모델 추론을 위한 입력데이터 생성
def test_data(OUTPUT_FILENAME, MODEL_NAME):
    tocompose = T.Compose([T.CenterCrop((200,330)),T.Resize((224,224)),T.ToTensor()])

    if (MODEL_NAME == "cough"): 
        MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"

        PATH = "./model/test/model_"
        MODEL_PATH  = PATH + MODEL_NAME + "_0908_v2.pt"
        model_cough = torch.load(MODEL_PATH, map_location='cpu')

        img_path = MELS_OUTPUT_FILENAME
        img_RGB  = Image.open(img_path).convert('RGB')
        img_compose = tocompose(img_RGB)
        img_data = torch.unsqueeze(img_compose, 0)
        
        with torch.no_grad():
            logit = model_cough(img_data)
            pred = logit.argmax(dim=1, keepdim=True)

    elif (MODEL_NAME == "corona"): 
        MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
        a = np.loadtxt(MFCC_OUTPUT_FILENAME, delimiter=",")
        b= torch.Tensor(a)

        PATH = "./model/test/model_"
        MODEL_PATH  = PATH + MODEL_NAME + "_0908_v2.pt"
        model_corona = torch.load(MODEL_PATH)
        
        with torch.no_grad():
            logit, value = model_corona(b)
            pred = logit.argmax(dim=1, keepdim=True)
    
    return pred



# 코로나 예측 모델 및 적용
def print_corona_prediction(OUTPUT_FILENAME):
    PATH0 = "save2"
    PATH1 = "save3"

    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
    MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"

    print("Corona_predict_Start")
    print("--------------------------")
    
    MODEL_NAME = "corona"
    predicted_vector = test_data(OUTPUT_FILENAME, MODEL_NAME)
    predicted_vector = predicted_vector[1]
    
    if (str(predicted_vector) == "tensor([0])"): 
        CLASS_NAME = "3"
        result = "기침소리 감지 - 이상없음"
        filename = OUTPUT_FILENAME +"_"+ str(CLASS_NAME)
        rename_file(OUTPUT_FILENAME, CLASS_NAME)
        print(result)
        
    elif(str(predicted_vector) == "tensor([1])"):
        CLASS_NAME = "2"
        result = "코로나 주의요망"
        filename = OUTPUT_FILENAME +"_"+ str(CLASS_NAME)
        rename_file(OUTPUT_FILENAME, CLASS_NAME)
        print(result)
        
    print("Corona_predict_End")
    print("--------------------------")
    print("--------------------------")
    print("--------------------------")

    return result, filename



# 기침 탐지 모델 및 적용
def print_cough_prediction(OUTPUT_FILENAME):
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
    MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"

    PATH0 = "save0"
    PATH1 = "save1"

    print("Cough_predict_Start")
    print("--------------------------")

    MODEL_NAME = "cough"
    predicted_vector = test_data(OUTPUT_FILENAME, MODEL_NAME)
    
    if (str(predicted_vector[0]) == "tensor([1])"): 
        CLASS_NAME = "1"
        result = "이상없음"
        filename = OUTPUT_FILENAME +"_"+ str(CLASS_NAME)
        rename_file(OUTPUT_FILENAME, CLASS_NAME)
        print(result)
        
    elif(str(predicted_vector[0]) == "tensor([0])"):
        CLASS_NAME = "0"
        result = "기침소리 감지"
        filename = OUTPUT_FILENAME +"_"+ str(CLASS_NAME)
        rename_file(OUTPUT_FILENAME, CLASS_NAME)
        print(result)
        result, filename= print_corona_prediction(OUTPUT_FILENAME +"_0")
        
    print("Cough_predict_End")
    print("--------------------------")

    return result, filename



# 멜스페트럼 생성
def extract_mels(OUTPUT_FILENAME):
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MELS_OUTPUT_FILENAME = OUTPUT_FILENAME +".png"
    
    print("--------------------------")
    print("Extract_features_MELS_Start")
    
    y,sr = librosa.load(WAVE_OUTPUT_FILENAME, sr=44100, mono=True)
    
    melspec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    log_melspec = librosa.power_to_db(melspec, ref=np.max)  
    librosa.display.specshow(log_melspec, sr=sr)

    plt.savefig(MELS_OUTPUT_FILENAME)
    plt.clf()
    print("Extract_features_MELS_End")
    print("--------------------------")
    
    result, filename = extract_mfcc(OUTPUT_FILENAME)

    return result, filename



# MFCC 생성
def extract_mfcc(OUTPUT_FILENAME):
    print("--------------------------")
    print("Extract_features_MFCC_Start")
    
    CFG = {
    'SR':22050,
    'N_MFCC':32, 
    'SEED':41
    }
    
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    MFCC_OUTPUT_FILENAME = OUTPUT_FILENAME +".csv"
    
    y, sr = librosa.load(WAVE_OUTPUT_FILENAME, sr=CFG['SR'])
    y_log = librosa.power_to_db(y, ref=np.max)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    rmse = librosa.feature.rms(y=y)       
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    mfcc = librosa.feature.mfcc(y =y_log, sr =sr, hop_length =1024, n_mfcc=13)
    delta1_mfcc = librosa.feature.delta(mfcc, order=1)
    delta2_mfcc = librosa.feature.delta(mfcc, order=2)

    empty=[np.mean(chroma_stft),np.mean(rmse),np.mean(spec_cent),np.mean(spec_bw),np.mean(rolloff),np.mean(zcr)]    
    for e in mfcc:
        empty.append(np.mean(e))
    for f in delta1_mfcc:
        empty.append(np.mean(f))
    for g in delta2_mfcc:
        empty.append(np.mean(g))
      
    empty_df=pd.DataFrame(empty).T
    
    empty_df.to_csv(MFCC_OUTPUT_FILENAME, index = False)


    print("Extract_features_MFCC_End")
    print("--------------------------")
    
    result, filename = print_cough_prediction(OUTPUT_FILENAME)
    
    return result, filename



# Reatime 사운드파일 생성
def audio_rec():
    TIME_FILENAME = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    OUTPUT_PATH = "./data_realtime"
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)

    OUTPUT_FILENAME = "./data_realtime/cough_test_"+TIME_FILENAME
    WAVE_OUTPUT_FILENAME = OUTPUT_FILENAME +".wav"
    IMAG_OUTPUT_FILENAME = OUTPUT_FILENAME +".jpg"
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

    print("Start to record the audio.")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording is finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print("Create " + WAVE_OUTPUT_FILENAME)

    result, filename = extract_mels(OUTPUT_FILENAME)
    
    return result, filename




