#####################################################
# Package:
# pip install pyaudio scipy matplotlib
#
# Usage:
# python recorder.py <folder_name> <subfolder_name (default: "")>
#
#####################################################

import sys
import pyaudio
from scipy.io.wavfile import write
import time
import csv
import wave
import os
import matplotlib.pyplot as plt

p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16

#--------global para--------
RATE = 16000
CHANNELS=2
CHUNK = 16
WIDTH = 2
FORMAT = pyaudio.paInt16
duration = 2  # seconds
filename_counter = 0
folder_name="Data"
buffer_size = 200
stream_list = []
#--------global para--------


if len(sys.argv)>1:
    folder_name = sys.argv[1]
subfolder_name = "1030"
if len(sys.argv)>2:
    subfolder_name = sys.argv[2]

def callback(in_data, frame_count, time_info, status):
    return (in_data, pyaudio.paContinue)

def makeStream(FORMAT, CHANNELS, RATE, INDEX, CHUNK):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index = INDEX,
                    frames_per_buffer=CHUNK)
    return stream

def runCommand(cmand):
    if cmand == 'h':
        printHelp()
    elif cmand == 'd':
        setDuration()
    elif cmand == 'n':
        setStartNumber()
    elif cmand == 'r':
        record_utterance()
    else:
        print('Error: Cammand not found!')

def printHelp():
    print('r: Recording n seconds audio')
    print('d: Setting duration for wav file')
    print('n: Setting starting number for filename')
    print('p: Set whether play after record (1 or 0)')
    print('ctrl+C: Exit')
    print('')

def setStartNumber():
    global filename_counter
    filename_counter = input('Name file starting at? (default 0): ')

def setDuration():
    global duration
    duration = input('Duration of wave file in seconds (default 2): ')

def record_utterance():
    global start_number
    global duration
    global RATE
    global CHUNK
    global duration
    global stream_list
    global folder_name
    global subfolder_name
    global CHANNELS
    global filename_counter
    '''
    for j in range(len(stream_list)):
        stream_list[j].start_stream()
    '''
    time.sleep(0.2)

    frames = [ [] for _ in range(len(stream_list))]
    for i in range(0, int(RATE / CHUNK * duration)):
        for j in range(len(stream_list)):
            #stream_list[j].start_stream()
            data = stream_list[j].read(CHUNK, exception_on_overflow = False)
            #stream_list[j].stop_stream()
            frames[j].append(data)
    
    filename = str(filename_counter)+'.wav'
    for i in range(len(stream_list)):
        wf = wave.open(os.path.join(folder_name, subfolder_name, str(i), filename), 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames[i]))
        wf.close()
    '''
    for j in range(len(stream_list)):
        stream_list[j].stop_stream()
    '''
    filename_counter += 1




def getDeviceInfo():
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            n = p.get_device_info_by_host_api_device_index(0, i).get('name')
            print("Input Device id ", i,"-", n.encode("utf8").decode("cp950", "ignore"))

if __name__ == '__main__':
    getDeviceInfo()
    number_of_mics = int(input('Number of Mics: '))
    index_of_mics = []
    for i in range(number_of_mics):
        stri = 'Index for ' + str(i) + '-th mics.'
        index_of_mics.append(int(input(stri)))
        stream_list.append(makeStream(FORMAT, CHANNELS, RATE, index_of_mics[-1],CHUNK))
        
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    if not os.path.exists(os.path.join(folder_name, subfolder_name)):
        os.makedirs(os.path.join(folder_name, subfolder_name))
    for i in range(number_of_mics):
        if not os.path.exists(os.path.join(folder_name, subfolder_name,str(i))):
            os.makedirs(os.path.join(folder_name, subfolder_name,str(i)))

    while True:
        try:
            task_command = input('Feed me a task (h for help): ')
            runCommand(task_command)
        except KeyboardInterrupt:
            for i in range(number_of_mics):
                stream_list[i].close()
            sys.exit()
