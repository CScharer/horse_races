import sys
from pathlib import Path
# from pydantic import BaseModel
# from typing import Optional
from PyQt6.QtGui import (
    QIcon,
    QPixmap
)
from PyQt6 import QtCore
from PyQt6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
    QSize
)
# from PyQt6.QtGui import QFocusEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QCommandLinkButton,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
from horse_races import (
    DEFAULT_BUY_IN,
    DEFAULT_SCRATCHED_HORSE_COST,
    DEFAULT_SCRATCHED_HORSE_ORDER,
    IMAGE_FILES,
    HorseGame,
    Player,
    Sort,
    clear_console
)

class CustomSlider(QSlider):
        def __init__(self, orientation, parent=None):
            super().__init__(orientation, parent)
            self.setMinimum(25)
            self.setMaximum(100)
            self.setValue(25)
            self.setTickInterval(25)
            self.setMouseTracking(True) # Enable mouse tracking

        def mouseMoveEvent(self, event):
            # Access mouse position: event.pos() for local coordinates, event.globalPos() for screen coordinates
            # Access mouse buttons pressed: event.buttons()
            # Perform actions based on mouse movement
            # print(f"Mouse moved to: {event.pos().x()}, {event.pos().y()}")
            super().mouseMoveEvent(event) # Call the base class implementation
            # print(f"self.value(): {self.value()}, {self.value() / self.minimum()}")


class MainWindow(QMainWindow):
    horse_game: HorseGame = None

    def __init__(self):
        super().__init__()
        horse_game: HorseGame = HorseGame(
            gui=self,
            by_in=DEFAULT_BUY_IN,
            scratched_horse_cost=DEFAULT_SCRATCHED_HORSE_COST,
            scratched_horse_order=DEFAULT_SCRATCHED_HORSE_ORDER
            )
        self.horse_game = horse_game
        self.setWindowTitle("Cattoors (NOT Kentucky OR Montucky) Derby")
        # self.setFixedSize(QSize(1380, 620))
        self.showMaximized()
        self.lbl = QLabel("<h1>Players</h1>")
        # self.lbl.setGeometry(QRect(10, 10, 200, 50))
        self.btn = QPushButton("Deal Cards")
        # self.btn.setGeometry(QRect(20, 10, 10, 10))
        self.btn.clicked.connect(self.btn_clicked)
        # self.btn.clicked.connect(
        #     lambda:self.lbl.setText("<h1>Button was clicked</h1>")
        # )
        layout = QVBoxLayout()
        layout.addWidget(self.lbl)

        self.lblScratchOrder = QLabel(parent=self)
        self.lblScratchOrder.setObjectName(f"lblScratchOrder")
        self.lblScratchOrder.setText(f"Scratch Order:")
        layout.addWidget(self.lblScratchOrder)
        self.cboScratchOrder = QComboBox(parent=self)
        self.cboScratchOrder.setObjectName(f"cboScratchOrder")
        # for option in options: cboScratchOrder.addItem(option)
        self.cboScratchOrder.addItems(Sort.all())
        self.cboScratchOrder.setCurrentIndex(Sort.all().index(horse_game.scratched_horse_order.value))
        self.cboScratchOrder.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus) # Set focus policy
        self.cboScratchOrder.setEditable(False)  # Make the combo box editable
        layout.addWidget(self.cboScratchOrder)


        self.lblBuyIn = QLabel(parent=self)
        self.lblBuyIn.setObjectName(f"lblBuyIn")
        self.lblBuyIn.setText(f"Buy In/Ante:")
        self.txtBuyIn = QLineEdit(parent=self)
        self.txtBuyIn.setObjectName(f"txtBuyIn")
        self.txtBuyIn.setText(f"{(DEFAULT_BUY_IN):,.2f}")
        layout.addWidget(self.lblBuyIn)
        layout.addWidget(self.txtBuyIn)

        self.lblScratchedHorseCost = QLabel(parent=self)
        self.lblScratchedHorseCost.setObjectName(f"lblScratchedHorseCost")
        self.lblScratchedHorseCost.setText(f"Scratched Horse Cost:")
        self.txtScratchedHorseCost = QLineEdit(parent=self)
        self.txtScratchedHorseCost.setObjectName(f"txtScratchedHorseCost")
        self.txtScratchedHorseCost.setText(f"0.25")
        layout.addWidget(self.lblScratchedHorseCost)
        layout.addWidget(self.txtScratchedHorseCost)

        self.lblSpeed = QLabel(parent=self)
        self.lblSpeed.setObjectName(f"lblSpeed")
        self.lblSpeed.setText(f"Speed:")
        self.slider: CustomSlider = CustomSlider(orientation=QtCore.Qt.Orientation.Horizontal, parent=self)
        layout.addWidget(self.lblSpeed)
        layout.addWidget(self.slider)

        # directory_path = Path("images")
        # files_only = [entry for entry in directory_path.iterdir() if entry.is_file()]

        for image_file in IMAGE_FILES:
            file_name: str = image_file.name
            # file_path_name: str = f"images/{file_name}"
            # button = QPushButton()
            # pixmap = QPixmap(file_path_name)
            # icon = QIcon(pixmap)
            # button.setIcon(icon)
            # button.setIconSize(QSize(64, 64))  # Adjust size as needed
            # button.clicked.connect(lambda checked, file=image_file: self.on_button_clicked(file))
            self.chkPlayer = QCheckBox(file_name.replace(".png", ""))
            self.chkPlayer.clicked.connect(lambda checked, file=image_file: self.on_checkbox_clicked(file))
            self.chkPlayer.setChecked(True)
            self.on_checkbox_clicked(image_file)  # Initialize checkbox state
            layout.addWidget(self.chkPlayer)
            # layout.addWidget(button)
            # self.checkbox.clicked.connect(lambda checked, file=image_file: self.on_button_clicked(file))
        layout.addWidget(self.btn)

        self.setLayout(layout)

        window = QWidget()
        window.setLayout(layout)
        self.setCentralWidget(window)

        # self.todo_form = ToDoForm(self.add_todo_to_list)
        # layout.addWidget(self.todo_form)
        # self.todo_table = ToDoTable()
        # layout.addWidget(self.todo_table)

    def on_checkbox_clicked(self, image_file):
        player_name: str = str(image_file).replace("images/", "").replace(".png", "")
        print(f"Checkbox clicked for: {player_name}")
        player_found: Player = None
        for player in self.horse_game.players:
            if player.name == player_name:
                player_found = player
                print(f"Found player: {player_name}")
                break
        if player_found:
            self.horse_game.remove_player(player_found.name)
            print(f"Removed player: {player_name}")
        else:
            print(f"Adding player: {player_name}")
            player_new = Player(name=player_name)
            self.horse_game.add_player(player=player_new)
            # self.horse_game.show_player(player)
        self.horse_game.show_players()

    def on_button_clicked(self, image_file):
        player_name: str = str(image_file).replace("images/", "").replace(".png", "")
        print(f"Button clicked for: {player_name}")

    def on_button_click(self):
        print("Image button clicked!")

    def btn_clicked(self):
        print(f"Button clicked: {self.btn.text()}")
        match self.btn.text():
            case "Deal Cards":
                self.horse_game.gui = self
                self.horse_game.by_in = float(self.txtBuyIn.text())
                self.horse_game.scratched_horse_cost = float(self.txtScratchedHorseCost.text())
                self.horse_game.scratched_horse_order = self.cboScratchOrder.currentText()
                self.horse_game.deal_cards(display=True)
                self.btn.setText("Scatch Horses")
            case "Scatch Horses":
                self.horse_game.scratch_horses()
                self.horse_game.show_horses_scratched()
                self.btn.setText("Play")
            case "Play":  
                self.horse_game.play()
                self.btn.setText("Play Again")
            # case "Show Winners":  
            #     self.horse_game.show_winners()
            #     self.btn.setText("Play Again")
            case "Play Again":  
                self.horse_game.reset()
                self.btn.setText("Deal Cards")
            case _:
                self.horse_game.show_winners()
        # if self.lbl.text() == "Deal Cards":
        #     self.horse_game.deal_cards()
        #     self.lbl.setText("<h1>Horses</h1>")
        # self.lbl.setText("<h1>Button was clicked</h1>")
        # self.horse_game.scratch_horses()
        # self.btn.setText("Thanks for clicking")

    def add_todo_to_list(self, name, completed):
        # Callback to add the todo item to the table
        self.todo_table.add_to_do_item(name, completed)


if __name__ == "__main__":
    clear_console()
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    # app = QApplication(sys.argv)
    # dialog = QDialog()
    # ui_dialog = Ui_Dialog()
    # ui_dialog.setupUi(dialog)
    # dialog.show()
    # sys.exit(app.exec())
