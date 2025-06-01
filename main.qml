import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 500
    color: "green"

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: homePage
    }

    Component {
        id: homePage
        Item {
            id: root
            Button {
                anchors.centerIn: parent
                text: "TASK RUNNER"
                onClicked: root.StackView.view.push("InputTaskPage.qml", StackView.Immediate)
            }
        }
    }
}