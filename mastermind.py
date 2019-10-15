import sys
import random

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

# Every Qt application must have one and only one QApplication object;
# it receives the command line arguments passed to the script, as they
# can be used to customize the application's appearance and behavior
qt_app = QtWidgets.QApplication(sys.argv)


class Mastermind(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Mastermind, self).__init__(parent)

        # list of possible pin colors
        self.colors = [
            "purple",
            "orange",
            "blue",
            "yellow",
            "red",
            "turquoise",
            "green",
            "pink"
        ]

        # Create table widget
        self.table_view = QtWidgets.QTableWidget()
        # Connect click event
        self.table_view.clicked.connect(self.clicked)
        # Remove edit triggers
        self.table_view.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )
        # Set focus policy
        self.table_view.setFocusPolicy(QtGui.Qt.NoFocus)
        # Pull palette
        palette = self.table_view.palette()
        # Tweak palette
        palette.setBrush(
            QtGui.QPalette.Highlight, QtGui.QBrush(QtGui.Qt.white)
        )
        palette.setBrush(
            QtGui.QPalette.HighlightedText, QtGui.QBrush(QtGui.Qt.black)
        )
        # Set palette after changes
        self.table_view.setPalette(palette)

        # Make widget stretch when resizing the view
        self.table_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.table_view.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # Hide headers
        self.table_view.horizontalHeader().hide()
        self.table_view.verticalHeader().hide()

        # Hide grid
        self.table_view.setShowGrid(False)

        # Create horizontal layout for buttons on bottom
        self.button_layout = QtWidgets.QHBoxLayout()

        # Create button to validate choice
        self.validate_button = QtWidgets.QPushButton("validate")
        self.validate_button.clicked.connect(self.validate)

        # Create button to restart game
        self.restart_button = QtWidgets.QPushButton("restart")
        self.restart_button.clicked.connect(self.restart)

        # Create main layout of the widget
        self.layout = QtWidgets.QVBoxLayout()
        # Add widgets to the window
        self.layout.addWidget(self.table_view)
        self.button_layout.addWidget(self.validate_button)
        self.button_layout.addWidget(self.restart_button)
        self.layout.addLayout(self.button_layout)

        # Game stuff
        # amount of guesses (-2)
        self.table_view.setRowCount(12)
        # amount of pins (-4)
        self.table_view.setColumnCount(8)
        # Initialize variable that will store pin selected by the user
        self.selected_color = ""
        # Pick secret code
        self.code = self.pick_code()
        self.choice = ["" for _ in range(self.table_view.columnCount() - 4)]
        print(self.code)

        self.rows_filled = 0

        self.setup_tableview()

        # Set window properties
        self.setWindowTitle("mastermind")
        scalar = 60
        self.setMinimumSize(
            self.table_view.columnCount()*scalar,
            self.table_view.rowCount()*scalar
        )
        self.setLayout(self.layout)

    def pick_code(self):
        return [
            self.colors[random.randrange(0, len(self.colors))]
            for _ in range(self.table_view.columnCount() - 4)
        ]

    def restart(self):
        # Initialize variable that will store pin selected by the user
        self.selected_color = ""

        # Pick secret code
        self.code = self.pick_code()
        self.choice = ["" for _ in range(self.table_view.columnCount() - 4)]

        print(self.code)

        self.rows_filled = 0
        self.setup_tableview()

    def draw_picture(self, row, col, image_path):
        # Create image as pixmap
        wrapped_image = QtGui.QPixmap(image_path)
        image_label = QtWidgets.QLabel(self)

        # Put image inside the label
        image_label.setPixmap(wrapped_image)
        # Make sure the image scales along
        image_label.setScaledContents(True)
        image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored,
            QtWidgets.QSizePolicy.Ignored
        )
        # Put image in the grid
        self.table_view.setCellWidget(row, col, image_label)

    def draw_empty_cell(self, row, col, choise_path, answer_path):
        image = True

        if col > 0 and col < self.table_view.columnCount() - 3:
            image_name = choise_path
        elif col == self.table_view.columnCount() - 2:
            image_name = answer_path
        else:
            image = False

        if image:
            self.draw_picture(row, col, "./data/%s.jpg" % image_name)

    def compare(self):
        any_matches = []
        perfect_matches = []

        for index, pin in enumerate(self.code):
            if pin in self.choice:
                if self.choice[index] == self.code[index]:
                    perfect_matches.append(pin)
                else:
                    any_matches.append(pin)

        image_name = "%dmatches_%dperfect" % (
            len(any_matches), len(perfect_matches)
        )

        self.draw_picture(
            self.table_view.rowCount()-2-self.rows_filled,
            self.table_view.columnCount() - 2,
            "./data/%s.jpg" % image_name
        )

        # if code is guessed or ran out of guesses
        if (
            len(perfect_matches) == (self.table_view.columnCount() - 4) or
            self.rows_filled == self.table_view.rowCount()-3
        ):
            return "Game Over"
        else:
            return "Next"

    def validate(self):
        if "" not in self.choice:
            # compare input vs secret code
            state = self.compare()

            if state != "Game Over":
                # increment rows filled
                self.rows_filled += 1

                # draw new row of answer cells
                for col in range(self.table_view.columnCount()):
                    self.draw_empty_cell(
                        self.table_view.rowCount()-2-self.rows_filled,
                        col,
                        "answer_main",
                        "answer_nomatches"
                    )
            else:
                # Draw correct combination on top
                for col in range(1, self.table_view.columnCount()-3):
                    self.draw_picture(
                        0,
                        col,
                        "./data/%s.jpg" % self.code[(col-1)]
                    )
            # reset self.choice list
            self.choice = [
                "" for _ in range(self.table_view.columnCount() - 4)
            ]
        else:
            print(
                "Please input all %d pins" % (self.table_view.columnCount()-4)
            )

    def setup_tableview(self):
        # Clear table
        self.table_view.clear()

        # Define row on which to put pins
        current_input_row = self.table_view.rowCount()-2-self.rows_filled

        for col in range(self.table_view.columnCount()):
            self.table_view.setColumnWidth(col, 20)

        for row in range(self.table_view.rowCount()):
            self.table_view.setRowHeight(row, 20)

            if row > 0 and row < current_input_row:
                for col in range(self.table_view.columnCount()):
                    self.draw_empty_cell(
                        row, col, "emptygrid_choices", "emptygrid_answers"
                    )

            elif row == current_input_row:
                for col in range(self.table_view.columnCount()):
                    self.draw_empty_cell(
                        row, col, "answer_main", "answer_nomatches"
                    )

            elif row == (self.table_view.rowCount()-1):
                # Put the choises
                begin_loop = int((self.table_view.columnCount() - 8) * 0.5)
                end_loop = begin_loop + 8
                for col in range(begin_loop, end_loop):
                    color = self.colors[col - begin_loop]
                    image_name = "./data/%s.jpg" % color

                    # Create image as pixmap
                    wrapped_image = QtGui.QPixmap(image_name)
                    image_label = QtWidgets.QLabel(self)

                    # Put image inside the label
                    image_label.setPixmap(wrapped_image)
                    # Make sure the image scales along
                    image_label.setScaledContents(True)
                    image_label.setSizePolicy(
                        QtWidgets.QSizePolicy.Ignored,
                        QtWidgets.QSizePolicy.Ignored
                    )
                    # Put image in the grid
                    self.table_view.setCellWidget(row, col, image_label)

    def clicked(self):
        # Get row and column of the selected cell
        row = self.table_view.selectedIndexes()[0].row()
        col = self.table_view.selectedIndexes()[0].column()

        begin_loop = int((self.table_view.columnCount() - 8) * 0.5)

        # Check if a column from the bottom row is clicked
        if row == (self.table_view.rowCount()-1):
            if col >= begin_loop and col < self.table_view.columnCount() - begin_loop:
                if self.selected_color != self.colors[col - begin_loop]:
                    if self.selected_color != "":
                        # Draw the old pin without the circle
                        self.draw_picture(
                            row,
                            self.colors.index(self.selected_color) + begin_loop,
                            "./data/%s.jpg" % self.selected_color
                        )
                    # Change the selected color variable
                    self.selected_color = self.colors[col - begin_loop]
                    # Draw the newly selected pin with the circle
                    self.draw_picture(
                        row, col, "./data/%s_picked.jpg" % self.selected_color
                    )
        elif row == (self.table_view.rowCount()-2-self.rows_filled):
            # Check for valid column to place input
            if col > 0 and col < self.table_view.columnCount() - 3:
                # Store the currently selected color in the list of choices
                self.choice[col-1] = self.selected_color
                # Draw the pin
                self.draw_picture(
                    row, col, "./data/%s_input.jpg" % self.selected_color
                )

    def run(self):
        # Show the window
        self.show()
        # Run the qt application
        qt_app.exec_()


mastermind = Mastermind()
mastermind.run()
