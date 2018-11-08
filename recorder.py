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
from scipy.io.wavfile import read as scipy_wave_read
import time
import csv
import timeit
import wave
import os
import matplotlib.pyplot as plt
import cv2

cap = cv2.VideoCapture(1)
CAPTURE_VIDEO = 1

p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16

#--------global para--------
RATE = 16000
CHANNELS=2
CHUNK = 4
WIDTH = 2
FORMAT = pyaudio.paInt16
duration = 1.25  # seconds
filename_counter = 0
folder_name="Training"
cam_folder_name = "Training_cam"
buffer_size = 200
stream_list = []
#--------global para--------

if len(sys.argv)>1:
    folder_name = sys.argv[1]
subfolder_name = "1030"
if len(sys.argv)>2:
    subfolder_name = sys.argv[2]

CAM_FOLDER = os.path.join(cam_folder_name, subfolder_name)

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
    elif cmand == 'r' or cmand == 'p':
        record_utterance()
    elif cmand == 'plt':
        show_last_waves()
    elif cmand == 'exit':
        sys.exit()
    else:
        print('Error: Cammand not found!')

def printHelp():
    print('r: Recording n seconds audio')
    print('d: Setting duration for wav file')
    print('n: Setting starting number for filename')
    print('plt: Plot the records')
    print('exit: Exit')
    print('')

def setStartNumber():
    global filename_counter
    filename_counter = input('Name file starting at? (default 0): ')
    filename_counter = int(filename_counter)

def setDuration():
    global duration
    duration = input('Duration of wave file in seconds (default 2): ')

def record_utterance():
    global duration
    global RATE
    global CHUNK
    global duration
    global stream_list
    global folder_name
    global subfolder_name
    global CHANNELS
    global filename_counter
    global CAM_FOLDER
    if not os.path.exists(os.path.join(CAM_FOLDER, str(filename_counter))):
        os.makedirs(os.path.join(CAM_FOLDER, str(filename_counter)))
    '''
    for j in range(len(stream_list)):
        stream_list[j].start_stream()
    '''
    time.sleep(0.2)
    
    frames = [ [] for _ in range(len(stream_list))]
    start = timeit.default_timer()
    for i in range(0, int(RATE / CHUNK * duration)):
        for j in range(len(stream_list)):
            #stream_list[j].start_stream()
            data = stream_list[j].read(CHUNK, exception_on_overflow = False)
            #stream_list[j].stop_stream()
            frames[j].append(data)
        
        if CAPTURE_VIDEO==1 and i % 400 ==0:
            record_image(os.path.join(CAM_FOLDER, str(filename_counter)), i//200)

    stop = timeit.default_timer()
    print('Finished: ', stop - start)

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

def show_last_waves():
    global folder_name
    global subfolder_name
    if filename_counter==0:
        print("Record Not Found!")
        return
    filename = str(filename_counter-1)+'.wav'
    for i in range(len(stream_list)):
        _fs, data = scipy_wave_read(os.path.join(folder_name, subfolder_name, str(i), filename))
        plt.subplot(int(len(stream_list)*100+10+i+1))
        plt.plot(data)

    plt.show()



def record_image(path, frame_index):
    global cap
    global CAM_FOLDER
    _ret, frame = cap.read()

    frame_name = os.path.join(path, str(frame_index)+'.jpg')
    cv2.imwrite(frame_name, frame)


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

    if CAPTURE_VIDEO==1:
        if not os.path.exists(cam_folder_name):
            os.makedirs(cam_folder_name)
        if not os.path.exists(os.path.join(cam_folder_name, subfolder_name)):
            os.makedirs(os.path.join(cam_folder_name, subfolder_name))

    while True:
        try:
            task_command = input('Feed me a task (h for help): ')
            runCommand(task_command)
        except KeyboardInterrupt:
            for i in range(number_of_mics):
                stream_list[i].close()
            sys.exit()
