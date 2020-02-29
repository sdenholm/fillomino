
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

import sys


from fillomino.display import MainApp

#board   = Board(10,10)
#display = Display(Board(10,10))
#display.run()

gui = MainApp()
gui.run()

#app = QApplication(sys.argv)
#windowExample = basicWindow()

"""
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec_()
"""