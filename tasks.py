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

    @Slot(str)
    def loadFromText(self, text):
        lines = text.splitlines()
        self.task = Task.from_lines(lines)
        self.currentInstruction = next(self.task.instructions())
