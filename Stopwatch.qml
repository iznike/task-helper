import QtQuick
import QtQuick.Controls

Label {
    id: stopwatch

    required property var timeFunction

    property alias running: timer.running

    horizontalAlignment: Text.AlignHCenter
    verticalAlignment: Text.AlignVCenter

    font.pointSize: 72
    fontSizeMode: Text.Fit
    font.family: "Courier New"

    text: "0:00:00.00"

    Timer {
        id: timer
        running: true
        triggeredOnStart: true
        repeat: true
        interval: 10
        onTriggered: {
            stopwatch.text = stopwatch.timeFunction();
        }
    }
}