import pyaudio
import wave

class RecAUD:

    def __init__(self, chunk=4096, frmat=pyaudio.paInt16, channels=1, rate=24000, py=pyaudio.PyAudio()):

        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 1
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
    
    def start_record(self):
        self.st = 1
        self.frames = []
        while self.st == 1:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

        self.stream.stop_stream()
        self.stream.close()

        wf = wave.open('recording.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        self.st = 0