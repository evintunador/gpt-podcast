from gtts import gTTS
import sys
from pydub import AudioSegment
import pygame


def preprocess_text(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    processed_text = text.replace('\n', ' ')
    with open(file_path, 'w') as file:
        file.write(processed_text)

def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")


def text_to_speech(file_path, output_path):
    preprocess_text(file_path)
    
    # Read content from file
    with open(file_path, 'r') as file:
        text = file.read()
    
    # Initialize gTTS object
    tts = gTTS(text=text, lang='en')
    
    # Save as MP3 file
    tts.save(output_path)

def play_audio(output_path):
    pygame.mixer.init()
    pygame.mixer.music.load(output_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python tts.py <input_file_path> <output_file_path>")
        print("Where the input is a .txt and the output is a .mp3")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Execute function
    text_to_speech(input_path, output_path)
    convert_mp3_to_wav(output_path, f"{output_path[:-4]}.wav")
    play_audio(output_path)
