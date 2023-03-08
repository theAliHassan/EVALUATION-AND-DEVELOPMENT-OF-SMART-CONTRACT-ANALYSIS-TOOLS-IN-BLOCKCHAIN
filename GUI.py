import sys
import csv
import subprocess
import datetime
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QPlainTextEdit, QFileDialog, QDialog
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPalette


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the background color of the GUI to dark blue
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background, QColor(0, 0, 50))
        self.setPalette(self.palette)

        # Set the font and color for the timer label
        font = QFont()
        font.setPointSize(16)
        self.timer_label = QLabel('00:00:00', self)
        self.timer_label.setFont(font)
        self.timer_label.setStyleSheet('color: red')
        #self.timer_label.setAlignment(0)

        # Create a dropdown menu to select an item
        self.item_label = QLabel('Select an item:', self)
        self.item_label.setStyleSheet('color: white')
        self.item_combo = QComboBox(self)
        self.item_combo.setStyleSheet('background-color: white')
        self.load_items()

        # Create a text box for the selected command
        self.command_label = QLabel('My command:', self)
        self.command_label.setStyleSheet('color: white')
        self.command_text = QPlainTextEdit(self)
        self.command_text.setStyleSheet('background-color: white')

        # Create a terminal window
        self.terminal_label = QLabel('Terminal:', self)
        self.terminal_label.setStyleSheet('color: white')
        self.terminal = QPlainTextEdit(self)
        self.terminal.setStyleSheet('background-color: black; color: white')
        self.terminal.setReadOnly(True)
        self.terminal.setUndoRedoEnabled(False)
        self.terminal.mousePressEvent = self.open_file

        # Create buttons
        self.analyze_button = QPushButton('Analyze', self)
        self.analyze_button.setStyleSheet('background-color: white')
        self.analyze_button.clicked.connect(self.execute_command)


        self.clear_button = QPushButton('Clear', self)
        self.clear_button.setStyleSheet('background-color: white')
        self.clear_button.clicked.connect(self.clear_gui)

        self.save_button = QPushButton('Save Results', self)
        self.save_button.setStyleSheet('background-color: white')
        self.save_button.clicked.connect(self.save_results)

        # Create a layout
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()

        hbox1.addWidget(self.timer_label)
        hbox1.addStretch(1)

        hbox2.addWidget(self.item_label)
        hbox2.addWidget(self.item_combo)
        hbox2.addStretch(1)

        hbox3.addWidget(self.command_label)
        hbox3.addWidget(self.command_text)
        hbox3.addStretch(1)

        hbox4.addWidget(self.terminal_label)
        hbox4.addWidget(self.terminal)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.analyze_button)
        vbox.addLayout(hbox4)
        vbox.addWidget(self.clear_button)
        vbox.addWidget(self.save_button)

        self.setLayout(vbox)

        # Set the window properties
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('GUI')
        self.show()

    def load_items(self):
        # Load the items from commands.csv
        with open('commands.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.item_combo.addItem(row[0], row[1])

    def execute_command(self):
        # Get the selected command from the dropdown menu
        command = self.item_combo.currentData()
        self.command_text.setPlainText(command)
        # Get the current time for the timer
        start_time = datetime.datetime.now()

        # Execute the command in the terminal window
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Update the terminal window with the output and error messages
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.terminal.setTextCursor(cursor)
        self.terminal.insertPlainText(output.decode('utf-8'))
        self.terminal.insertPlainText(error.decode('utf-8'))

        # Update the timer with the elapsed time
        elapsed_time = datetime.datetime.now() - start_time
        self.timer_label.setText(str(elapsed_time))

    def clear_gui(self):
        # Clear the text boxes and terminal window
        self.command_text.clear()
        self.terminal.clear()

    def save_results(self):
        # Get the selected item and command, and the output from the terminal window
        item = self.item_combo.currentText()
        command = self.command_text.toPlainText()
        output = self.terminal.toPlainText()

        # Save the results to a CSV file
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Results', '', 'CSV Files (*.csv)')
        if filename:
            with open(filename, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Smart Contract Name', 'Command', 'Results'])
                writer.writerow([item, command, output])

    def open_file(self, event):
        # Check if terminal has text, and get selected item from dropdown
        if self.terminal.toPlainText() != "":
            index = self.item_combo.currentIndex()
            item = self.item_combo.itemText(index)
            # If an item is selected, open corresponding Python file
            if item:
                print(item)
                item = item.replace(" ", "")
                print(item)
                filename = item + ".py"
                file_path = os.path.join(os.getcwd(), filename)
                # Create a new window to show the file
                file_window = QDialog(self)
                file_window.setWindowTitle(filename)
                file_window.resize(800, 600)
                # Create a text edit widget to show the file content
                file_content = QTextEdit(file_window)
                file_content.setReadOnly(True)
                with open(file_path, 'r') as f:
                    content = f.read()
                    file_content.setText(content)
                # Add the text edit widget to the window
                layout = QVBoxLayout()
                layout.addWidget(file_content)
                file_window.setLayout(layout)
                # Show the window
                file_window.show()

        # Call base class event handler to allow normal clicking behavior
        super().mousePressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
