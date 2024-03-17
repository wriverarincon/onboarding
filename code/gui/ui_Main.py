from PySide6.QtCore import (Qt)
from PySide6.QtGui import (QTextOption)
from PySide6.QtWidgets import (QLabel, QMainWindow, QVBoxLayout,
    QPushButton, QWidget, QTextEdit, QStackedWidget, QApplication)

class OnboardingUI(QMainWindow):
    '''
    Onboarding page, after introducing the necessary data the program will continue to set
    the needed profiles in both Cisco Webex and Calabrio.
    '''

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Onboarding')
        self.resize(800, 600)
        self.setMaximumSize(800, 600)

        # The window itself
        self.onboardingWindow = QWidget(self)

        # Storage variables
        self._count = 0
        self.agentEmail = []
        self.agentSchedule = []
        self.agentTeam = []
        self._data = []
        # self.tablePopup = TablePopup()

        # Widgets
        self.mainWidget = QWidget(self.onboardingWindow)
        self.contentWidget = QWidget(self.mainWidget)

        # Layouts
        self.onboardingWindowLayout = QVBoxLayout(self.onboardingWindow)
        self.onboardingWindowLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.contentLayout = QVBoxLayout(self.contentWidget)

        # Widgets
        self.mainWidget.setFixedSize(300, 124)
        # self.stackWidget.addWidget(self.tablePopup)

        # Content objects
        self.label = QLabel(self.contentWidget)
        self.inputBox = QTextEdit(self.contentWidget)
        self.submitBttn = QPushButton('Submit', self.contentWidget)
        self.submitBttn.setObjectName('submitBttn')

        # Content
            # Label
        self.label.setStyleSheet('font: 30px;')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText('Enter <span style="color: skyblue;">Emails</span>')
            
            # Input box
        self.inputBox.setFixedHeight(self.inputBox.document().size().height())
        self.inputBox.setWordWrapMode(QTextOption.NoWrap)
        self.inputBox.textChanged.connect(self.resizeBox)

            # Submit button
        self.submitBttn.setFixedWidth(100)
        self.submitBttn.setCursor(Qt.PointingHandCursor)
        self.submitBttn.clicked.connect(self.getText)

        # Add layouts
        self.onboardingWindowLayout.addWidget(self.mainWidget)
        self.mainLayout.addWidget(self.contentWidget)

        # Add content
        self.contentLayout.addWidget(self.label)
        self.contentLayout.addWidget(self.inputBox)
        self.mainLayout.addWidget(self.submitBttn, alignment=Qt.AlignCenter)

        self.setCentralWidget(self.onboardingWindow)

    def resizeBox(self):
        preferredHeight = self.inputBox.document().size().height()
        MAXIMUM_HEIGHT = 400

        if preferredHeight <= MAXIMUM_HEIGHT:
            self.inputBox.setFixedHeight(preferredHeight)
            self.mainWidget.setFixedHeight(preferredHeight + 120)
        else:
            self.inputBox.setFixedHeight(MAXIMUM_HEIGHT)

    def getText(self):
        text = self.inputBox.toPlainText()
        if self._count == 0:
            self._count = 1
            self.agentEmail = text
            self.inputBox.clear()
            self.label.setText(f'Enter <span style="color: skyblue;">Schedules</span>')

        elif self._count == 1:
            self._count = 2
            self.inputBox.clear()
            self.agentSchedule = text
            self.label.setText('Enter <span style="color: skyblue;">Teams</span>')

        elif self._count == 2:
            self._count = 3
            self.inputBox.clear()
            self.agentTeam = text

            self.showTable([(self.agentEmail), (self.agentSchedule), (self.agentTeam)])

    def showTable(self, data):
        # self.stackWidget.setCurrentIndex(1)
        import pages
        table = pages.TablePopup(data)
        done = table.exec()
        if done:
            pass
        else:
            self._count = 0
            self.label.setText('Enter <span style="color: skyblue;">Emails</span>')
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main = OnboardingUI()
    main.show()

    with open(r'code\gui\style\style_sheet.qss', 'r') as f:
        app.setStyleSheet(f.read())

    app.exec()