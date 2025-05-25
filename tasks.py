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
        self._overall_time = 0

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
    def overall_time(self):
        """returns the overall time taken for the task, in seconds"""
        if self.steps:
            return sum(self.step_times())
        else:
            return self._overall_time
    @overall_time.setter
    def overall_time(self, time):
        self._overall_time = time
    
    def step_times(self):
        """returns an array with the number of seconds each step took"""
        return [step.overall_time for step in self.steps]
    
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

class TaskRunnerException(Exception):
    pass

@QmlElement
class TaskRunner(QObject):

    currentInstructionChanged = Signal()
    runningChanged = Signal()
    finishedChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_instruction = ""
        self.timer = QElapsedTimer()
        self._running = False
        self._finished = False
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

    @Property(bool, notify=finishedChanged)
    def finished(self):
        return self._finished
    @finished.setter
    def finished(self, f):
        self._finished = f
        self.finishedChanged.emit()
        if f:
            for s in self.task.steps:
                print(f"{s.title}: {s.overall_time}s")

    def update_time(self, step: Task):
        """ adds the time elapsed since current_start_time to the step's overall_time, and updates current_start_time """
        end_time = self.timer.elapsed()
        step.overall_time += (end_time - self.current_start_time) / 1000
        self.current_start_time = end_time

    @Slot()
    def start(self):
        if self.running:
            raise TaskRunnerException("Start called on a TaskRunner that is already running")
        self.running = True
        self.finished = False   # in case it's being restarted

        # get list of steps
        self.steps = list(self.task.instructions(as_strings=False))
        self.stepIndex = 0

        # start timer and get first instruction
        self.timer.start()
        self.current_start_time = self.timer.elapsed()
        self.currentInstruction = self.steps[0].title

    @Slot()
    def next(self):
        if not self.running:
            raise TaskRunnerException("Next called on a TaskRunner that is not running")
        
        # update time for current step
        try:
            self.update_time(self.steps[self.stepIndex])
        except IndexError:  # IndexError here means stepIndex has already been incremented past the max, meaning it has already finished
            return

        # increment step
        self.stepIndex += 1
        try:
            self.currentInstruction = self.steps[self.stepIndex].title
        except IndexError:  # IndexError here means stepIndex has just been incremented past the max, meaning the last step is finished
            self.finished = True
            self.currentInstruction = ""

    @Slot()
    def back(self):
        if not self.running:
            raise TaskRunnerException("Back called on a TaskRunner that is not running")
        
        # update time for current step or last step if it was already finished
        if self.finished:
            self.finished = False
            self.update_time(self.steps[-1])
        else:
            self.update_time(self.steps[self.stepIndex])

        # decrement step
        if self.stepIndex != 0:
            self.stepIndex -= 1
            self.currentInstruction = self.steps[self.stepIndex].title

    @Slot()
    def stop(self):
        if not self.running:
            raise TaskRunnerException("Stop called on a TaskRunner that is not running")

        # if it hasn't finished, update the time before stopping
        if not self.finished:
            self.update_time(self.steps[self.stepIndex])

        self.running = False

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
        """ returns the total time of the current step so far, formatted as a string """
        # create a timedelta from the step's current overall_time (seconds) and the ms since current_start_time
        # plus 1 microsecond to ensure it's always formatted with fractional seconds
        s = self.steps[self.stepIndex].overall_time
        ms = self.timer.elapsed() - self.current_start_time
        td = timedelta(seconds=s, milliseconds=ms, microseconds=1)

        # return the string representation, truncated to 100th of a second
        return str(td)[:-4]
