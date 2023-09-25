import openai
import argparse
from pydub import AudioSegment
from config import API_KEY

def transcribe_audio(audio_path, output_path, api_key):
    # Read audio from given path
    audio = AudioSegment.from_wav(audio_path)

    # Convert audio to FLAC format
    audio_flac = audio.export("temp.flac", format="flac")
    
    # Set API key
    openai.api_key = api_key

    # Transcribe audio
    transcript = openai.Audio.transcribe('whisper-1', audio_flac)

    # Save transcript to output file
    with open(output_path, 'w') as file:
        file.write(transcript['text'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio to text.')
    parser.add_argument('audio_path', help='Path to the audio file (.wav).')
    parser.add_argument('output_path', help='Path to save the full transcript.')

    args = parser.parse_args()

    if API_KEY == '':
        print("API key not found in config.py. Exiting.")
        exit(1)

    transcribe_audio(args.audio_path, args.output_path, API_KEY)


    