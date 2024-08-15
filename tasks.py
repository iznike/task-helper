from PySide6.QtCore import QObject, Signal, Slot, Property, QElapsedTimer
from PySide6.QtQml import QmlNamedElement, QmlElement, qmlRegisterType

QML_IMPORT_NAME = "tasks"
QML_IMPORT_MAJOR_VERSION = 1

class Task:

    def __init__(self, title, steps = []):
        self.title = title
        self.steps = steps
        for i, step in enumerate(steps):
            if isinstance(step, str):
                self.steps[i] = Task(step)

    def instructions(self, timer=None):
        """generator function that recursively yields each instruction and records the elapsed time for each of them"""
        # for each step, record the time and yield the next instruction
        if timer: self.start_time = timer.elapsed()
        if len(self.steps) == 0:
            yield self.title
        else:
            for step in self.steps:
                yield from step.instructions(timer)
        # record final elapsed time after last step
        if timer: self.end_time = timer.elapsed()

    def overall_time(self):
        """returns the overall time taken for the task, in seconds"""
        if not hasattr(self, '_overall_time'):
            self._overall_time = (self.end_time - self.start_time) / 1000
        return self._overall_time
    
    def step_times(self):
        """returns an array with the number of seconds each step took"""
        times = []
        for step in self.steps:
            times.append(step.overall_time())
        return times
    
    def to_dict(self):
        pass
    
# load_from_plaintext()
# load_from_file()
# loadFromFile()


# class TaskRunner
# QtObject
# run()

@QmlElement
class TaskRunner(QObject):

    currentInstructionChanged = Signal()
    runningChanged = Signal()
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_instruction = ""
        self.timer = QElapsedTimer()
        self._running = False
        # hardcoded task for now
        self.task = Task("My fun task", [
            "Wash your hands",
            "Dry your hands",
            "Repeat",
            "End :)"
        ])

    @Property(str, notify=currentInstructionChanged)
    def currentInstruction(self):
        return self._current_instruction
    @currentInstruction.setter
    def currentInstruction(self, instruction):
        self._current_instruction = instruction
        self.currentInstructionChanged.emit()

    @Property(bool, notify=runningChanged)
    def running(self):
        return self._running
    @running.setter
    def running(self, r):
        self._running = r
        self.runningChanged.emit()

    @Slot()
    def start(self):
        if self.running:
            raise Exception("Already running")
        self.running = True

        # instantiate generator
        self.instructions_gen = self.task.instructions(self.timer)

        # start timer and get first instruction
        self.timer.start()
        self.currentInstruction = next(self.instructions_gen)

    @Slot()
    def next(self):
        if not self.running:
            raise Exception("Not running")
        
        try:
            self.currentInstruction = next(self.instructions_gen)
        except StopIteration:
            self.running = False
            self.currentInstruction = ""
            self.finished.emit()