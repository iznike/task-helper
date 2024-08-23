import time
import pytest
from PySide6.QtCore import QElapsedTimer
from PySide6.QtTest import QSignalSpy
from tasks import *

def list_of_instructions_test():
    task = Task("task", ["step 1", Task("task2", ["step 2.1", "step 2.2"]), "step 3", Task("task3", ["step 4"])])
    result = list(task.instructions())
    assert result == ["step 1", "step 2.1", "step 2.2", "step 3", "step 4"]

def list_of_tasks_test():
    task = Task("task", ["step 1", Task("task2", ["step 2.1", "step 2.2"]), "step 3", Task("task3", ["step 4"])])
    result = list(task.instructions(as_strings=False))
    assert result == [Task("step 1"), Task("step 2.1"), Task("step 2.2"), Task("step 3"), Task("step 4")]

def title_if_no_steps_test():
    instruction1 = "step 1"
    instruction2 = "step 2"
    task = Task("task", [Task(title=instruction1), Task(title=instruction2)])
    result = list(task.instructions())
    assert result == [instruction1, instruction2]

def task_eq_test():
    task1 = Task("title", [Task("1", ["1.1"]), Task("2")])
    task2 = Task("title", [Task("1", ["1.1"]), Task("2")])
    assert task1 == task2

def task_not_eq_test():
    task1 = Task("title", [Task("1", ["1.1"]), Task("2")])
    task2 = Task("title", [Task("1"), Task("2")])
    assert task1 != task2

def task_repr_test():
    task = Task("title", [Task("1", ["1.1"], 1), Task("2", depth=1)])
    expected = "Task(title='title', depth=0, steps=[Task(title='1', depth=1, steps=[Task(title='1.1', depth=2, steps=[])]), Task(title='2', depth=1, steps=[])])"
    assert repr(task) == expected

def load_from_lines_flat_test():
    lines = [
        "I am a title",
        "instruction 1",
        "instruction 2",
        "instruction 3"
    ]
    expected = Task("I am a title", steps=[Task("instruction 1"), Task("instruction 2"), Task("instruction 3")])

    result = Task.from_lines(lines)
    assert result == expected

def load_from_lines_nested_test():
    lines = [
        "I am a title",
        "instruction 1",
        "subtask 2",
        "\tsubsubtask 2.1",
        "\t\tinstruction 2.1.1",
        "\tinstruction 2.2",
        "instruction 3"
    ]
    expected = Task("I am a title", [
        Task("instruction 1"),
        Task("subtask 2", [
            Task("subsubtask 2.1", [
                Task("instruction 2.1.1")
            ]),
            Task("instruction 2.2")
        ]),
        Task("instruction 3")
    ])

    result = Task.from_lines(lines)

    assert list(result.instructions()) == ["instruction 1", "instruction 2.1.1", "instruction 2.2", "instruction 3"]
    assert result == expected


def current_instruction_property_signal_test():
    runner = TaskRunner()
    signal = QSignalSpy(runner.currentInstructionChanged)
    assert signal.isValid()
    runner.currentInstruction = "hello"
    assert signal.count() == 1
    assert runner.currentInstruction == "hello"

def current_instruction_changes_while_running_test():
    runner = TaskRunner()
    runner.task = Task("my test task", [Task("one"), Task("two")])
    signal = QSignalSpy(runner.finished)
    assert signal.isValid()

    assert runner.currentInstruction == ""
    assert runner.running == False

    runner.start()
    assert runner.currentInstruction == "one"
    assert runner.running == True

    runner.next()
    assert runner.currentInstruction == "two"
    assert runner.running == True
    assert signal.count() == 0

    runner.next()
    assert runner.currentInstruction == ""
    assert runner.running == False
    assert signal.count() == 1

def current_instruction_back_test():
    runner = TaskRunner()
    runner.task = Task("my test task", [Task("one", ["one part 1", "one part 2"]), Task("two", ["two part 1", "two part 2"])])

    runner.start()
    assert runner.currentInstruction == "one part 1"

    runner.back()
    assert runner.currentInstruction == "one part 1"

    runner.next()
    runner.next()
    runner.next()
    assert runner.currentInstruction == "two part 2"

    runner.back()
    assert runner.currentInstruction == "two part 1"

    runner.back()
    assert runner.currentInstruction == "one part 2"

    runner.back()
    assert runner.currentInstruction == "one part 1"

def start_raises_exception_if_already_running_test():
    runner = TaskRunner()
    runner.task = Task("my test task", [Task("one"), Task("two")])
    runner.start()

    with pytest.raises(Exception):
        runner.start()

def next_raises_exception_if_not_running_test():
    runner = TaskRunner()
    runner.task = Task("my test task", [Task("one"), Task("two")])

    with pytest.raises(Exception):
        runner.next()

def back_raises_exception_if_not_running_test():
    runner = TaskRunner()
    runner.task = Task("my test task", [Task("one"), Task("two")])

    with pytest.raises(Exception):
        runner.back()

def load_from_text_test():
    text = "I am a title\nInstruction 1\nSubtask\n\tInstruction 2\n\tInstruction 3\nInstruction 4"
    expected = Task("I am a title", [
        Task("Instruction 1", depth=1),
        Task("Subtask", depth=1, steps=[Task("Instruction 2", depth=2), Task("Instruction 3", depth=2)]),
        Task("Instruction 4", depth=1)
    ])
    runner = TaskRunner()

    runner.loadFromText(text)
    assert runner.task == expected
    assert runner.currentInstruction == "Instruction 1"

def task_times_test():
    # arrange
    task2 = Task("task2", ["step 2.1", "step 2.2"])
    task3 = Task("task3", ["step 4"])
    task = Task("task", ["step 1", task2, "step 3", task3])
    runner = TaskRunner()
    runner.task = task
    
    # act
    runner.start()
    time.sleep(1)
    runner.next()
    time.sleep(1)
    runner.next()
    time.sleep(2)
    runner.next()
    time.sleep(3)
    runner.next()
    time.sleep(2)
    runner.next()
    with pytest.raises(Exception):
        runner.next()

    # assert
    assert task.overall_time() == pytest.approx(9, abs=0.01), f"Top level task's overall time {task.overall_time()} does not match the expected value of 9"
    assert task.step_times() == pytest.approx([1, 3, 3, 2], abs=0.01), f"Top level task's step times {task.step_times()} do not match expected times of [1, 3, 3, 2].\nElapsed times are {[task.start_time, task.end_time]}"

    assert task2.overall_time() == pytest.approx(3, abs=0.01), f"First subtask's overall time {task2.overall_time()} does not match expected time of 3"
    assert task2.step_times() == pytest.approx([1, 2], abs=0.01), f"First subtask's step times {task2.step_times()} do not match expected times of [1, 2].\nElapsed times are {[task.start_time, task.end_time]}"

    assert task3.overall_time() == pytest.approx(2, abs=0.01), f"Second subtask's overall time {task3.overall_time()} does not match expected time of 2"
    assert task3.step_times() == pytest.approx([2], abs=0.01), f"Second subtask's step times {task3.step_times()} do not match expected times of [2].\nElapsed times are {[task.start_time, task.end_time]}"

def back_times_test():
    # arrange
    task = Task("task", ["step 1", "step 2"])
    runner = TaskRunner()
    runner.task = task

    # act
    runner.start()
    time.sleep(1)
    runner.next()
    time.sleep(1)
    runner.back()
    time.sleep(1)
    runner.next()
    time.sleep(1)
    runner.next()
    with pytest.raises(Exception):
        runner.next()

    # assert
    assert task.overall_time() == pytest.approx(4, abs=0.01)
    assert task.step_times() == pytest.approx([3, 1], abs=0.01)

def current_overall_time_test():
    # arrange
    task = Task("task", ["step 1", "step 2"])
    runner = TaskRunner()
    runner.task = task

    # act
    runner.start()
    time.sleep(1)
    runner.next()
    time.sleep(1)
    result = runner.currentOverallTimeString()

    # assert
    # assert result == pytest.approx(2, abs=0.01)
    assert result == "0:00:02.00"

def current_step_time_test():
    # arrange
    task = Task("task", ["step 1", "step 2"])
    runner = TaskRunner()
    runner.task = task

    # act
    runner.start()
    time.sleep(1)
    runner.next()
    time.sleep(1)
    result = runner.currentStepTimeString()

    # assert
    # assert result == pytest.approx(1, abs=0.01)
    assert result == "0:00:01.00"