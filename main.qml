import QtQuick
import QtQuick.Controls

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
        Item {
            Button {
                width: 50
                height: 25
                anchors.centerIn: parent
                text: "START"
                onClicked: pageLoader.source = "RunTaskPage.qml"
            }
        }
        
    }
    
}