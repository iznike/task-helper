import numpy as np

class Task:

    def __init__(self, title, steps = []):
        self.title = title
        self.steps = steps
        self.elapsed = np.empty(len(self.steps) + 1)

    def instructions(self, timer=None):
        """generator function that recursively yields each instruction and records the elapsed time for each of them"""
        # for each step, record the time and yield the next instruction
        for i, step in enumerate(self.steps):
            if timer: self.elapsed[i] = timer.elapsed()
            if isinstance(step, str):
                yield step
            else:
                yield from step.instructions(timer)
        # record final elapsed time after last step
        if timer: self.elapsed[len(self.steps)] = timer.elapsed()
        self.complete = True

    def overall_time(self):
        """returns the overall time taken for the task, in seconds"""
        return (self.elapsed[len(self.steps)] - self.elapsed[0]) / 1000
    
    def step_times(self):
        """returns an array with the number of seconds each step took"""
        return np.diff(self.elapsed) / 1000
    
    def to_dict(self):
        pass
    

# class TaskRunner
# QtObject
# load_from_plaintext()
# load_from_file()
# loadFromFile()
# run()

