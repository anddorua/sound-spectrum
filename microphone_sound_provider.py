import pyaudio;
import threading
import queue

class MicrophoneSoundProvider:
    def __init__(self, 
                 format: int = pyaudio.paInt16, 
                 channels: int = 1, 
                 rate: int = 44100, 
                 chunk: int = 1024):
        self._format = format
        self._channels = channels
        self._rate = rate
        self._chunk = chunk

    def openStream(self) -> queue.Queue:
        self._stream = pyaudio.PyAudio().open(format=self._format,
                                              channels=self._channels,
                                              rate=self._rate,
                                              input=True,
                                              frames_per_buffer=self._chunk)
        self._audioQueue = queue.Queue()
        self._stopEvent = threading.Event()
        self._audioProcessingThread = threading.Thread(target=self._audioProcessingThread)
        self._audioProcessingThread.start()
        return self._audioQueue
        
    def closeStream(self):
        self._stopEvent.set()
        self._audioProcessingThread.join()
        self._stream.stop_stream()
        self._stream.close()

    def _audioProcessingThread(self):
        while not self._stopEvent.is_set():
            data = self._stream.read(self._chunk, exception_on_overflow=False)
            self._audioQueue.put(data)
