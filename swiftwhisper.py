#!/usr/bin/env python3
import whisper, os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

Model = 'small'
English = False
Translate = False
SampleRate = 44100
BlockSize = 30
Threshold = 0.1
Vocals = [50, 1000]
EndBlocks = 40

class StreamHandler:
    def __init__(self, assist=None):
        if assist == None:
            class fakeAsst(): running, talking, analyze = True, False, None
            self.asst = fakeAsst()
        else:
            self.asst = assist
        self.running = True
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False
        print("Loading Whisper Model..", end='', flush=True)
        self.model = whisper.load_model(f'{Model}{".en" if English else ""}')
        print(" Done.")

    def callback(self, indata, frames, time, status):
        if not any(indata):
            print('.', end='', flush=True)
            return
        freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * SampleRate / frames
        if np.sqrt(np.mean(indata**2)) > Threshold and Vocals[0] <= freq <= Vocals[1] and not self.asst.talking:
            print('.', end='', flush=True)
            if self.padding < 1:
                self.buffer = self.prevblock.copy()
            self.buffer = np.concatenate((self.buffer, indata))
            self.padding = EndBlocks
        else:
            self.padding -= 1
            if self.padding > 1:
                self.buffer = np.concatenate((self.buffer, indata))
            elif self.padding < 1 < self.buffer.shape[0] > SampleRate:
                self.fileready = True
                write('dictate.wav', SampleRate, self.buffer)
                self.buffer = np.zeros((0,1))
            elif self.padding < 1 < self.buffer.shape[0] < SampleRate:
                self.buffer = np.zeros((0,1))
                print("\033[2K\033[0G", end='', flush=True)
            else:
                self.prevblock = indata.copy()

    def process(self):
        if self.fileready:
            print("\nTranscribing..")
            lang = 'en' if English else None
            result = self.model.transcribe('dictate.wav', fp16=False, language=lang, task='translate' if Translate else 'transcribe')
            print(f"\033[1A\033[2K\033[0G{result['text']}")
            if self.asst.analyze != None:
                self.asst.analyze(result['text'])
            self.fileready = False

    def listen(self):
        print("Listening.. (Ctrl+C to Quit)")
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(SampleRate * BlockSize / 1000), samplerate=SampleRate):
            while self.running and self.asst.running:
                self.process()

def main():
    try:
        handler = StreamHandler()
        handler.listen()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\nQuitting..")
        if os.path.exists('dictate.wav'):
            os.remove('dictate.wav')

if __name__ == '__main__':
    main()


