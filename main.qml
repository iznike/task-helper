import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 500
    color: "green"

    Loader {
        id: pageLoader
        anchors.fill: parent
        sourceComponent: startPage
    }

    Component {
        id: startPage
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
                onClicked: pageLoader.setSource("RunTaskPage.qml", {"taskText": taskText.text})
            }
        }
        
    }
    
}