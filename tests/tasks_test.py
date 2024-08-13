import time
import pytest
from PySide6.QtCore import QElapsedTimer
from tasks import *

def list_of_instructions_test():
    task = Task("task", ["step 1", Task("task2", ["step 2.1", "step 2.2"]), "step 3", Task("task3", ["step 4"])])
    result = list(task.instructions())
    assert result == ["step 1", "step 2.1", "step 2.2", "step 3", "step 4"]

def task_times_test():
    # arrange
    timer = QElapsedTimer()
    task2 = Task("task2", ["step 2.1", "step 2.2"])
    task3 = Task("task3", ["step 4"])
    task = Task("task", ["step 1", task2, "step 3", task3])
    
    # act
    result = task.instructions(timer)
    timer.start()
    next(result)
    time.sleep(1)
    next(result)
    time.sleep(1)
    next(result)
    time.sleep(2)
    next(result)
    time.sleep(3)
    next(result)
    time.sleep(2)
    with pytest.raises(StopIteration):
        next(result)

    # assert
    assert task.overall_time() == pytest.approx(9, abs=0.01), f"Top level task's overall time {task.overall_time()} does not match the expected value of 9"
    assert task.step_times() == pytest.approx([1, 3, 3, 2], abs=0.01), f"Top level task's step times {task.step_times()} do not match expected times of [1, 3, 3, 2].\nElapsed times are {[task.start_time, task.end_time]}"

    assert task2.overall_time() == pytest.approx(3, abs=0.01), f"First subtask's overall time {task2.overall_time()} does not match expected time of 3"
    assert task2.step_times() == pytest.approx([1, 2], abs=0.01), f"First subtask's step times {task2.step_times()} do not match expected times of [1, 2].\nElapsed times are {[task.start_time, task.end_time]}"

    assert task3.overall_time() == pytest.approx(2, abs=0.01), f"Second subtask's overall time {task3.overall_time()} does not match expected time of 2"
    assert task3.step_times() == pytest.approx([2], abs=0.01), f"Second subtask's step times {task3.step_times()} do not match expected times of [2].\nElapsed times are {[task.start_time, task.end_time]}"

def title_if_no_steps_test():
    instruction1 = "step 1"
    instruction2 = "step 2"
    task = Task("task", [Task(title=instruction1), Task(title=instruction2)])
    result = list(task.instructions())
    assert result == [instruction1, instruction2]