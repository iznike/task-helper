import QtQuick
import QtQuick.Controls
import QtTextToSpeech
import tasks

Item {
        anchors.fill: parent

        property string taskText
    
        TaskRunner {
            id: taskRunner
            onCurrentInstructionChanged: tts.say(taskRunner.currentInstruction)
        }

        Keys.onPressed: (event) => {
            if ((event.key == Qt.Key_Right) && (taskRunner.running)) {
                taskRunner.next();
            }
            if (event.key == Qt.Key_Space) {
                tts.say(instructionText.text);
            }
        }

        Text {
            id: instructionText
            focus: true
            anchors.fill: parent
            padding: 50
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            
            text: taskRunner ? taskRunner.currentInstruction : ""

            font.pointSize: 72
            fontSizeMode: Text.Fit
        }

        TextToSpeech {
            id: tts
        }

        Component.onCompleted: {
            taskRunner.loadFromText(taskText);
            taskRunner.start();
        }
    }