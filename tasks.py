from datetime import timedelta
from PySide6.QtCore import QObject, Signal, Slot, Property, QElapsedTimer
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "tasks"
QML_IMPORT_MAJOR_VERSION = 1

class Task:

    def __init__(self, title, steps=None, depth=0):
        self.title = title
        self.steps = steps if steps is not None else []
        self.depth = depth
        for i, step in enumerate(self.steps):
            if isinstance(step, str):
                self.steps[i] = Task(step, depth=self.depth+1)

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title!r}, depth={self.depth!r}, steps={self.steps!r})"

    def __eq__(self, other):
        if self.title != other.title:
            return False
        return self.steps == other.steps

    def instructions(self, as_strings=True):
        """generator function that recursively yields each step/instruction"""
        if len(self.steps) == 0:
            if as_strings:
                yield self.title
            else:
                yield self
        else:
            for step in self.steps:
                yield from step.instructions(as_strings)

    @property
    def start_time(self):
        if hasattr(self, '_start_time'):
            return self._start_time
        else:
            return self.steps[0].start_time
    @start_time.setter
    def start_time(self, time):
        self._start_time = time

    @property
    def end_time(self):
        if hasattr(self, '_end_time'):
            return self._end_time
        else:
            return self.steps[len(self.steps)-1].end_time
    @end_time.setter
    def end_time(self, time):
        self._end_time = time

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
    
    @classmethod
    def from_lines(cls, lines) -> 'Task':
        task_stack = []
        for i, line in enumerate(lines):
            # skip line if all whitespace
            if line == "" or line.isspace():
                continue
            # first line is the title of the top level task
            if i == 0:
                task_stack.append(cls(line.strip(), depth=0))
            else:
                # count how many tabs to get depth
                # (steps of the top level task have no tabs but a depth of 1)
                depth = 1
                while line[depth-1] == '\t':
                    depth += 1
                # create new task with stripped line as title
                new_task = cls(line.strip(), depth=depth)
                # pop off stack until the top task has 1 less depth
                while task_stack[-1].depth >= depth:
                    task_stack.pop()
                # append new task to steps, and push to stack
                task_stack[-1].steps.append(new_task)
                task_stack.append(new_task)
        # return top level task
        return task_stack[0]
    
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
        self.task = Task("Default Task")

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

        # get list of steps
        self.steps = list(self.task.instructions(as_strings=False))
        self.stepIndex = 0

        # start timer and get first instruction
        currentStep = self.steps[0]
        self.timer.start()
        currentStep.start_time = self.timer.elapsed()
        self.currentInstruction = currentStep.title

    @Slot()
    def next(self):
        if not self.running:
            raise Exception("Not running")
        
        # record end time for current step
        self.steps[self.stepIndex].end_time = self.timer.elapsed()

        # increment step and record start time
        self.stepIndex += 1
        try:
            step = self.steps[self.stepIndex]
            step.start_time = self.timer.elapsed()
            self.currentInstruction = step.title
        except IndexError:
            self.running = False
            self.currentInstruction = ""
            self.finished.emit()

    @Slot()
    def back(self):
        if not self.running:
            raise Exception("Not running")
        
        if self.stepIndex != 0:
            self.stepIndex -= 1
            self.currentInstruction = self.steps[self.stepIndex].title

    @Slot(str)
    def loadFromText(self, text):
        lines = text.splitlines()
        self.task = Task.from_lines(lines)
        self.currentInstruction = next(self.task.instructions(as_strings=True))

    @Slot(result=str)
    def currentOverallTimeString(self):
        """ returns the time since the task was started, formatted as a string """
        # create a timedelta from the milliseconds
        # plus 1 microsecond to ensure it's always formatted with fractional seconds
        td = timedelta(milliseconds=self.timer.elapsed(), microseconds=1)

        # return the string representation, truncated to 100th of a second
        return str(td)[:-4]
    
    @Slot(result=str)
    def currentStepTimeString(self):
        """ returns the time since the current step was started, formatted as a string """
        # create a timedelta from the milliseconds
        # plus 1 microsecond to ensure it's always formatted with fractional seconds
        ms = (self.timer.elapsed() - self.steps[self.stepIndex].start_time)
        td = timedelta(milliseconds=ms, microseconds=1)

        # return the string representation, truncated to 100th of a second
        return str(td)[:-4]
