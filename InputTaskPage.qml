import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    ColumnLayout {
        anchors.fill: parent
        TextArea {
            id: taskText
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.margins: 10
        }
        Button {
            width: 50
            height: 25
            Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
            Layout.bottomMargin: 10
            text: "START"
            onClicked: root.StackView.view.push("RunTaskPage.qml", {"taskText": taskText.text})
        }
    }        
}