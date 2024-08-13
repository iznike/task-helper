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
    

# class TaskRunner
# QtObject
# load_from_plaintext()
# load_from_file()
# loadFromFile()
# run()

