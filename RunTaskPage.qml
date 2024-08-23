import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtTextToSpeech
import tasks

Item {
    anchors.fill: parent

    property string taskText

    ColumnLayout {
        anchors.fill: parent
        Text {
            id: instructionText
            focus: true
            Layout.fillWidth: true
            Layout.fillHeight: true
            padding: 50
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            
            text: taskRunner ? taskRunner.currentInstruction : ""

            font.pointSize: 72
            fontSizeMode: Text.Fit
            wrapMode: Text.Wrap
        }

        ColumnLayout {
            id: timers
            Layout.fillWidth: false
            Layout.fillHeight: false
            Layout.preferredWidth: parent.width/2
            Layout.preferredHeight: parent.height/3
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

            Stopwatch {
                id: overallStopwatch
                Layout.fillWidth: true
                Layout.fillHeight: true
                running: taskRunner ? taskRunner.running : false
                timeFunction: function () { return taskRunner.currentOverallTimeString() }
            }

            Stopwatch {
                id: stepStopwatch
                Layout.fillWidth: false
                Layout.preferredWidth: overallStopwatch.width/2
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignHCenter
                running: taskRunner ? taskRunner.running : false
                timeFunction: function () { return taskRunner.currentStepTimeString() }
            }
            
        }

    }

    TaskRunner {
        id: taskRunner
        onCurrentInstructionChanged: tts.say(taskRunner.currentInstruction)
    }

    Keys.onPressed: (event) => {
        if ((event.key == Qt.Key_Right) && (taskRunner.running)) {
            taskRunner.next();
        }
        if ((event.key == Qt.Key_Left) && (taskRunner.running)) {
            taskRunner.back();
        }
        if (event.key == Qt.Key_Space) {
            tts.say(instructionText.text);
        }
    }

    TextToSpeech {
        id: tts
    }

    Component.onCompleted: {
        taskRunner.loadFromText(taskText);
        taskRunner.start();
    }
}