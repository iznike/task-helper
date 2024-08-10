import QtQuick
import QtQuick.Controls
import QtTextToSpeech

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 500
    color: "green"

    property list<string> steps: [
        "Wash your hands",
        "Dry your hands",
        "Repeat",
        "End :)"
    ]

    Text {
        focus: true
        anchors.fill: parent
        padding: 50
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        
        property int step: 1
        text: root.steps[step]

        font.pointSize: 72
        fontSizeMode: Text.Fit

        Keys.onPressed: (event) => {
            if ((event.key == Qt.Key_Right) && (step < root.steps.length - 1))
                step++;
            if ((event.key == Qt.Key_Left) && (step > 0))
                step--;
            if (event.key == Qt.Key_Space) {
                tts.say(text);
            }
        }
    }

    TextToSpeech {
        id: tts
    }
}