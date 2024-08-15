import QtQuick
import QtQuick.Controls
import QtTextToSpeech
import tasks

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 500
    color: "green"

    TaskRunner { id: taskRunner }

    Button {
        text: "START"
        onClicked: {
            taskRunner.start();
            visible = false;
            instructionText.focus = true;
        }
    }

    Text {
        id: instructionText
        focus: true
        anchors.fill: parent
        padding: 50
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        
        text: taskRunner.currentInstruction

        font.pointSize: 72
        fontSizeMode: Text.Fit

        Keys.onPressed: (event) => {
            if ((event.key == Qt.Key_Right) && (taskRunner.running)) {
                taskRunner.next();
                tts.say(text);
            }
            if (event.key == Qt.Key_Space) {
                tts.say(text);
            }
        }
    }

    TextToSpeech {
        id: tts
    }
}