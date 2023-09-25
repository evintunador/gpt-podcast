### EXECUTIVE SUMMARY

This repo creates a little app that lets me have a podcast with ChatGPT as my co-host. The codebase is awful but functional as is everything I make.

# Installation instructions

1. Clone the repo to your local machine
2. Good luck figuring out all the required python packages
3. Open `config.py` and paste in your OpenAI `API_KEY`. Also feel free to edit the prompt or model being used.

# How to use

1. Navigate to the repo in your terminal
2. Run `python main.py`
3. Hit the `Start/Stop Recording` button to begin recording. If your mic has two channels this whole thing will probably break.
4. Hit the `Start/Stop Recording` button to end recording.
5. Hit the `Transcribe Recording` button to send the recording through OpenAI's WhisperAPI to transcribe it.
6. Hit the `Get Response` button to send the transcription through ChatGPT for a response.
7. Hit the `Create & Speak Response` button to create an audio recording of ChatGPT's response and have it spoken out loud to you. 
   - I am sorry for the shitty tts engine I used, planning to switch to a high quality API that used a transformer model in the future.
8. Repeat steps 3-8 until your podcast is over
9. Share the files `full_recording.wav` and `full_transcript.txt` on your podcast platform of choice.
