from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QPushButton, QTableWidgetItem, QTableWidget, QHBoxLayout, QDialog)

class TablePopup(QDialog):
    '''
    Shows data introduced in the onboarding page for confirmation.
    '''

    windowTitle = 'Data Showcase'
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle('Data Showcase')
        self.setMaximumSize(800, 600)

        # Layouts
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        tableWidget = QTableWidget()
        tableWidget.setColumnCount(3)

        # Widgets
        tableWidget.setFixedHeight(500)
        headers = ['Emails', 'Schedules', 'Teams']
        tableWidget.setHorizontalHeaderLabels(headers)

        # Buttons
        correct = QPushButton('Correct!')
        incorrect = QPushButton('Redo it')
        incorrect.setObjectName('incorrectBttn')
        
        for bttn in [correct, incorrect]:
            bttn.setFixedSize(100, 30)
            bttn.setCursor(Qt.PointingHandCursor)
            bttn.clicked.connect(self.bttnClicked)

        data = [i.split('\n') for i in data]
        tableWidget.setRowCount(len(data[0]))
        for column, var in enumerate(data):
            for row, value in enumerate(var):
                item = QTableWidgetItem(str(value))
                tableWidget.setItem(row, column, item)

        layout.addWidget(tableWidget)
        layout.addWidget(correct)
        layout.addWidget(incorrect)
        self.setLayout(layout)
        
        tableWidget.resizeColumnsToContents()

        tableWidget.setFixedWidth(tableWidget.viewportSizeHint().width() + 20)

    def bttnClicked(self):
        sender = self.sender()
        if sender.text() == 'Correct!':
            return self.accept()
        elif sender.text() == 'Redo it':
            return self.reject()
