import queue, json
import sounddevice as sd
import threading
from vosk import Model, KaldiRecognizer
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "listener"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class CommandListener(QObject):
    
    command = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.q = queue.Queue()
        self.model = Model(r".\vosk-model-small-en-us-0.15")

    @Property(list)
    def commands(self):
        return self._commands
    @commands.setter
    def commands(self, new):
        self._commands = new
        self.words = new + ["[unk]"]

    @Property(bool)
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self, new):
        self._enabled = new
        
    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(bytes(indata))
        
    def listen(self):
        with sd.RawInputStream(blocksize=8000, dtype="int16", channels=1, callback=self.callback) as stream:
            rec = KaldiRecognizer(self.model, stream.samplerate, json.dumps(self.words))
            while self.enabled:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())['text']
                    if result in self.commands:
                        self.command.emit(result)
                        print(result)
                        rec = KaldiRecognizer(self.model, stream.samplerate, json.dumps(self.words))

    @Slot()
    def start(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

# l = CommandListener()
# l.commands = ["next", "back"]
# l.enabled = True
# l.listen()