import tkinter as tk
import time
from recorder import RecAUD
import threading
from transcriber import transcribe_audio
from config import *
import response as rsp
import openai
import tts
import os
import wave


### Keeps track of the full transcript & audio recording

# Initialize or reset 'full_transcript.txt'
if os.path.exists('full_transcript.txt'):
    if os.path.getsize('full_transcript.txt') > 0:
        os.remove('full_transcript.txt')

with open('full_transcript.txt', 'w') as f:
    pass

def append_transcript_to_full(transcript_filename, human_input=True):
    # to make it clear who's talking when reading the transcript
    string_to_append = "\n\nHuman:\n" if human_input else "\n\nPodcastGPT:\n"

    # Append regular string to 'full_transcript.txt'
    with open('full_transcript.txt', 'a') as full_transcript:
        full_transcript.write(string_to_append)

    # Append content of given transcript file to 'full_transcript.txt'
    with open(transcript_filename, 'r') as transcript, open('full_transcript.txt', 'a') as full_transcript:
        for line in transcript:
            full_transcript.write(line)


# delete 'full_recording.wav' if it already exists from prior run
if os.path.exists('full_recording.wav'):
    if os.path.getsize('full_recording.wav') > 0:
        os.remove('full_recording.wav')

# Hardcoded parameters (Example: 1 channel, 2 bytes wide, 44100 sample rate)
params = (1, 2, 44100, 0, 'NONE', 'not compressed')

with wave.open('full_recording.wav', 'wb') as full_audio:
    full_audio.setparams(params)

def append_audio_to_full(audio_filename):
    # Load parameters and data from source WAV file
    with wave.open(audio_filename, 'rb') as src_audio:
        params = src_audio.getparams()
        audio_data = src_audio.readframes(params.nframes)

    # Initialize or read existing full audio
    full_audio_data = b""
    if os.path.exists('full_recording.wav') and os.path.getsize('full_recording.wav') > 44: # Skip header size
        with wave.open('full_recording.wav', 'rb') as full_audio:
            full_audio_data = full_audio.readframes(full_audio.getnframes())

    # Concatenate audio data
    full_audio_data += audio_data
    # Write concatenated audio data
    with wave.open('full_recording.wav', 'wb') as full_audio:
        full_audio.setparams(params)
        full_audio.writeframes(full_audio_data)



### records the user's voice

# Global variables to maintain state
audio_recorder = None
start_thread = None
stop_flag = threading.Event()  # Shared flag

def countdown_timer(duration):
    text_widget.insert(tk.END, f"You have a limited amount of time to speak!!!!\nUnfortunately the speech-to-text API has a filesize limit :(\nTime remaining: 4m 30s\n")
    start_time = time.time()
    end_time = start_time + duration
    next_print = start_time + 30  # Next time to print remaining time
    
    while not stop_flag.is_set() and time.time() < end_time:
        if time.time() >= next_print:
            remaining_time = int(end_time - time.time())
            minutes, seconds = divmod(remaining_time, 60)
            text_widget.insert(tk.END, f"Time remaining: {minutes}m {seconds}s\n")
            next_print += 30

def toggle():
    global audio_recorder, start_thread, stop_flag
    
    if audio_recorder is None:
        text_widget.insert(tk.END, f"Recording started at {time.time()}\n")

        # Reset stop_flag
        stop_flag.clear()

        # Create an instance of your RecAUD class
        audio_recorder = RecAUD()

        # Start the recording in a new thread
        start_thread = threading.Thread(target=audio_recorder.start_record)
        start_thread.start()

        # Initialize countdown timer
        duration = 4 * 60 + 30  # 4 minutes and 30 seconds
        timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
        timer_thread.start()

    else:
        text_widget.insert(tk.END, f"Recording stopped at {time.time()}\n")

        # Stop the recording
        audio_recorder.stop_record()

        # Signal to stop the timer
        stop_flag.set()

        # Wait for the start_thread to finish
        start_thread.join()

        # Reset state
        audio_recorder = None
        start_thread = None

        append_audio_to_full('recording.wav')



### transcribes the audio file

def transcribe():
    text_widget.insert(tk.END, f"Audio transcribed at {time.time()}\n")

    # no point in calling if there's no API key
    if API_KEY == '':
        print("API key not found in config.py. Exiting.")
        text_widget.insert(tk.END, f"API key not found in config.py. Exiting.")
        exit(1)

    # Define the path to the audio file and where you'd like to save the transcript
    audio_path = "recording.wav"
    output_path = "transcript.txt"

    # Call the function
    transcribe_audio(audio_path, output_path, API_KEY)  

    # append human speech to the full text transcript
    append_transcript_to_full('transcript.txt', human_input=True)



### gets response from chatGPT API

# pretty sure this should be a global variable
if len(context) > rsp.context_len:
    context = context[0:rsp.context_len]
ALL_MESSAGES = [{'role':'system', 'content': context}]

def answer():
    global ALL_MESSAGES

    # checks for api key
    if API_KEY == '':
        print("API key not found in config.py. Exiting.")
        text_widget.insert(tk.END, f"API key not found in config.py. Exiting.")
        exit(1)
    openai.api_key = API_KEY

    # grabs newest user speech and appends it to the conversation
    text = rsp.open_file('transcript.txt')
    if text == '':
        # empty submission. Probably hit the button too early by accident
        print("No transcribed response to continue conversation with. Exiting.")
        text_widget.insert(tk.END, f"No transcribed response to continue conversation with. Exiting.")
        exit(1)
    ALL_MESSAGES.append({'role': 'user', 'content': text})

    # gets chatGPT's response
    response, tokens = rsp.chatbot(ALL_MESSAGES)
    if tokens >= rsp.max_tokens[model]:
        a = ALL_MESSAGES.pop(1)
    ALL_MESSAGES.append({'role': 'assistant', 'content': response})
    
    # saves chatGPT's response to a txt file to be read by the text-to-speech engine
    rsp.save_file('response.txt', response)

    # append gpt response to the full text transcript
    append_transcript_to_full('response.txt', human_input=False)



### reads off response

def txt2spch():
    #text_widget.insert(tk.END, f"Function z called at {time.time()}\n")
    tts.text_to_speech('response.txt', 'response.mp3')
    tts.convert_mp3_to_wav('response.mp3', 'response.wav')
    tts.play_audio('response.mp3')

    append_audio_to_full('response.wav')




# Close window when 'esc' is pressed
def close_window(event):
    root.quit()

# Initialize Tkinter window
root = tk.Tk()
root.title("GPT Podcast")
root.minsize(300, 200)  # Set minimum size: width 300, height 200

# Add buttons
#button_listen_hotkey = tk.Button(root, text="Trigger listen_hotkey (BROKEN)", command=listen_hotkey)
#button_listen_hotkey.pack()
button_toggle = tk.Button(root, text="Start/Stop Recording", command=toggle)
button_toggle.pack()
button_transcribe = tk.Button(root, text="Transcribe Recording", command=transcribe)
button_transcribe.pack()
button_answer = tk.Button(root, text="Get Response", command=answer)
button_answer.pack()
button_tts = tk.Button(root, text="Create & Speak Response", command=txt2spch)
button_tts.pack()

# Add Text widget for output
text_widget = tk.Text(root, wrap='word', height=10, width=40)
text_widget.pack()
text_widget.insert(tk.END, f"GPT Podcaster initialized at {time.time()}\n")

# Run Tkinter event loop
root.mainloop()





