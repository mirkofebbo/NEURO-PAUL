"""
Version:  Python 3.8.10
Created on Wed Feb 15 2023

This is a simple lsl UI that send and log timestamps. 
The user can send triggers and custom message,
while the code will be sending a "heartbeat" timestamp every 5 second for post-sync
The UI offer a log window that display the past messages sent.
The file is saved localy once the window is closed

@author: Mirko Febbo

python 3.10

conda install pandas
conda install -c tstenner pylsl 
conda install pysimplegui
conda install -c conda-forge pygame 


"""
import os
import time
from datetime import date # Save the data file with the current date
import pandas as pd
import threading  
# GUI LIB
import PySimpleGUI as sg # Gui library 
# LSL LIB
from pylsl import StreamInfo, StreamOutlet, StreamInlet, IRREGULAR_RATE
import argparse
import signal
# SOUND
# import pygame
import random


# SOUND VAL
# pygame.init()
# pygame.mixer.init()
# sound = pygame.mixer.Sound('audio/beep-01.mp3') # Load audio file 
# sound.set_volume(0.2)   # Now plays at 20% of full volume.
is_auto_beep = False
print( "\a")


#GENERAL MSG VAL 
message = ""
#FIRST H MSG 
heartbeat_update = time.time()

# ---- LOAD/CREATE LOCAL LOG FILE ----------------------------------------
today = date.today() # Load today info 
file_path = f'data/{today}.csv' # Create the file path 
if(os.path.exists(file_path)):
    # If the fill exist create a new entry 
    humain_time = time.strftime("%H:%M:%S", time.localtime()) # Human readable time 
    temp_data = [time.time_ns(), str(humain_time), "APP START"] # First log 
    df = pd.read_csv(file_path, index_col=False) # Load the file   
    df.loc[len(df.index)] = temp_data  # Global val 
else:
    # else create the file  
    humain_time = time.strftime("%H:%M:%S", time.localtime()) # Human readable time 
    temp_data = [[time.time_ns(), str(humain_time), "APP START" ]] # First log 
    df = pd.DataFrame(temp_data, columns=['ux time', 'human time', 'message'])  # Create the DF  
    df.to_csv(file_path, index=False) # Save the file   
    
# ---- THEME SETUP ----------------------------------------
# Create a custom theme in pysimplegui
# This theme is inspired form the Matrix movie and classic hacker screen since it is simple and readable
sg.set_options(font= "ModeSeven 12")
sg.LOOK_AND_FEEL_TABLE['my_matrix_theme'] = {'BACKGROUND': '#0D0208',
                                        'TEXT': '#00FF41',
                                        'INPUT': '#202729',
                                        'TEXT_INPUT': '#008F11',
                                        'SCROLL': '#008F11',
                                        'BUTTON': ('#0D0208', '#00FF41'),
                                        'PROGRESS': ('#D1826B', '#CC8019'),
                                        'BORDER': 0, 
                                        'SLIDER_DEPTH': 0, 
                                        'PROGRESS_DEPTH': 0,
                                        }
sg.theme('my_matrix_theme')
# ---- LSL ----------------------------------------
# Timstamp call function
def send_lsl_timestamp(outlet):
    # SEND LSL TIMESTAMP to TABLET
    my_message = f'{message} t:{time.time_ns()}' # log custom message with time it was sent
    outlet.push_sample([my_message])
    return
# Timestamp thread
class thread_send_lsl_timestamp(threading.Thread):
    # send the LSL MSG using threading
    def __init__(self, threadID, name, counter, outlet, message): 
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.outlet = outlet
        self.message =  message
        
    def run(self):
        print ("Starting " + self.name)
        eval(self.name+'(self.outlet)')
        print ("Exiting " + self.name)

# Quiting if needed
def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
# START TIMESTAMPS THREAD
def start_timestamp_threads(message, threadID):
    # Encopass the start of the timestamping threads for the phone and tablet 
    clicked_time = time.time_ns()
    humain_time = time.strftime("%H:%M:%S", time.localtime())
    temp_data = [clicked_time, humain_time, message]
    # Start the timestamp threading
    tablet = thread_send_lsl_timestamp(threadID, "send_lsl_timestamp" ,threadID, outlet, message)
    tablet.start()
    # Log the timestamp to screen
    df.loc[len(df.index)] = temp_data
    window["-LOGBOX-"].print(temp_data)

    return 
# Create the LSL com
parser = argparse.ArgumentParser(description="Stream heartbeat clock and annotation with LSL")
parser.add_argument("--source", default="MirkoMac", help="the name of the source (this) machine")
parser.add_argument("--id", default="Mirko_id", help="the id of the LSL")

args = parser.parse_args()
info = StreamInfo(args.source, 'Markers', 1, 0, 'string', args.id)
outlet = StreamOutlet(info)
signal.signal(signal.SIGINT, handler) 

# ---- AUDIO ----------------------------------------
def call_random_function():
    # Radomly play the sound every 4-8 second 
    while is_auto_beep:
        time.sleep(random.randint(4, 8))
        sound.play() 
        clicked_time = time.time_ns()
        humain_time = time.strftime("%H:%M:%S", time.localtime())
        temp_data = [clicked_time, humain_time, 'AUTO_BEEP']
        # Log the timestamp to screen
        df.loc[len(df.index)] = temp_data
        window["-LOGBOX-"].print(temp_data)


# ---- LAYOUT SETUP ----------------------------------------
# Here you can play by adding buttons, text and more 
layout = [
    [ sg.Button("TRIGGER", key="-TRIGGER-"),
        sg.Button("BEEP", key="-BEEP-"), sg.Button("AUTO BEEP ON", key="-AUTO_BEEP-"), 
        sg.Button("RECORDING ON", key="-RECORDING-")],
    [ sg.HSeparator()],
    [ sg.Button("MAKE", key="-MAKE-"), sg.Button("MISS", key="-MISS-"), sg.Button("RELEASE", key="-RELEASE-")],
    [ sg.HSeparator()],

    [ sg.Button("SEND", key="-SEND-", bind_return_key=True), sg.Input("",key="-MESSAGE-")],
    [ sg.HSeparator()],
    [sg.Multiline(size=(66,10), key='-LOGBOX-')]
    ]
# Displaying it to the window
window = sg.Window("TEST V10", layout, keep_on_top=True, location = (705, 125))

while True:
    
    event, values = window.read(timeout=1000)
# --------------- USER EVENT ---------------
    # Pick up if the user has clicked something
    # CLOSING EVENT
    if event == sg.WIN_CLOSED:
        df.to_csv(file_path, index=False)
        is_auto_beep = False
        is_recording = False
        start_timestamp_threads('APP END', "END")  
        print("---------DATA SAVED------------")
        break
    # SEND TRIGGER 
    if event == "-TRIGGER-":
        message = "TRIGGER"
        start_timestamp_threads(message, "TRIGGER")    
    # MAKE BEEP
    if event == "-BEEP-":
        sound.play() 
        message = "BEEP"
        start_timestamp_threads(message, "BEEP")  
    # AUTO BEEP
    if event == "-AUTO_BEEP-":
        is_auto_beep    =   not is_auto_beep
        if is_auto_beep:    
            window['-AUTO_BEEP-'].update('AUTO BEEP OFF')
            message = "AUTO BEEP START"
        else:               
            window['-AUTO_BEEP-'].update('AUTO BEEP ON')
            message = "AUTO BEEP ENDS"

        threading.Thread(target=call_random_function).start()
        start_timestamp_threads(message, "AUTO_BEEP")  
    # VIDEO RECORDING
    if event == "-RECORDING-":
        is_auto_beep    =   not is_auto_beep
        if is_auto_beep:    
            window['-RECORDING-'].update('RECORDING OFF')
            message = "RECORDING START"
        else:               
            window['-RECORDING-'].update('RECORDING ON')
            message = "RECORDING END"
        start_timestamp_threads(message, "RECORDING")  

    # SEND CUSTOM EVENT
    if event == "-SEND-" :
        print(values)
        message = values["-MESSAGE-"]
        start_timestamp_threads(message, "MESSAGE")
        window["-MESSAGE-"].update("")
 
    # BALL 
    if event == "-MAKE-" :
        message = "MAKE"
        start_timestamp_threads(message, "MESSAGE")
    if event == "-MISS-" :
        message = "MISS"
        start_timestamp_threads(message, "MESSAGE")
    if event == "-RELEASE-" :
        message = "RELEASE"
        start_timestamp_threads(message, "MESSAGE")
# --------------- AUTO UPDATE ---------------
    # HEARTBEAT UPDATE
    # Send a msg automaticaly every 5 second
    if(time.time() - heartbeat_update > 5):
        message = "H"
        start_timestamp_threads(message, "HEARTBEAT")   
        heartbeat_update = time.time()

window.close