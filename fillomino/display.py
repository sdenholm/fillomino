import logging
logger = logging.getLogger(__name__)

import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

import numpy as np

import PyQt5.QtWidgets as QtWidgets


class GUI(QtCore.QObject):
  """
  """
  
  
  
  #CELL_STYLE_NORMAL      = "border-style: outset; border-width: 1px; border-color: black; background: white;"
  #CELL_STYLE_HIGHLIGHTED = "border-style: outset; border-width: 1px; border-color: yellow; background: yellow;"
  
  class SelectedCell(object):
    def __init__(self, x, y, originalStyle):
      self.x = x
      self.y = y
      self.originalStyle = originalStyle
  
  # initial setup
  def __init__(self, controller, board):
    """ GUI initialisation """
    
    super().__init__()
    
    # references to controller and the board to display
    self.controller = controller
    self.board      = None
    
    # highlighted/selected cell
    self.selectedCell = None
    
    # get boad dimensions
    rows, columns = board.getBoardDimensions()
    


    

    ###########################################################################
    # define stylesheets for text and the game cells
    ###########################################################################

    # text styles
    #  -initial are underlined, others are normal
    self.TEXT_STYLE_NORMAL  = ""
    self.TEXT_STYLE_INITIAL = " text-decoration: underline; "
    
    # cell styles
    defaultCellStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.CELL_STYLE_INITIAL     = defaultCellStyle + " background: linen; "
    self.CELL_STYLE_NORMAL      = defaultCellStyle + " background: white; "
    self.CELL_STYLE_HIGHLIGHTED = defaultCellStyle + " background: yellow; "
    
    # group cell styles
    self.CELL_STYLE_1 = defaultCellStyle+"background: powderblue;"
    self.CELL_STYLE_2 = defaultCellStyle+"background: cornsilk;"
    self.CELL_STYLE_3 = defaultCellStyle+"background: khaki;"
    self.CELL_STYLE_4 = defaultCellStyle+"background: lightskyblue;"
    self.CELL_STYLE_5 = defaultCellStyle+"background: aquamarine;"
    self.CELL_STYLE_6 = defaultCellStyle+"background: thistle;"
    self.CELL_STYLE_7 = defaultCellStyle+"background: moccasin;"
    self.CELL_STYLE_8 = defaultCellStyle+"background: lightsteelblue;"
    self.CELL_STYLE_9 = defaultCellStyle+"background: palegreen;"
    
    # invalid group styles
    self.CELL_STYLE_INVALID = defaultCellStyle+"background: crimson;"
    
    
    ###########################################################################
    # define keys
    ###########################################################################
    

    # backspace and delete
    self.DELETE_KEY_LIST = [16777219, 16777223]
    
    # 1 to 9
    self.NUMBER_KEY_LIST = list(range(49, 58))
    
    # 87: w
    # 65: a
    # 83: s
    # 68: d

    ###########################################################################
    # create the GUI
    ###########################################################################

    
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    self.mainWindow = QtWidgets.QWidget()
    
    # set window size and title
    self.mainWindow.resize(35*rows, 35*columns)
    self.mainWindow.setWindowTitle("Fillomino v0.1")
    
    # register function for keyboard presses
    self.mainWindow.keyPressEvent = self._keyPressed
    
    # use a box layout for the other layouts
    self.mainLayout = QtWidgets.QVBoxLayout()
    self.mainWindow.setLayout(self.mainLayout)
    
    # menu bar
    menuLayout = self._createMenuBar()
    self.mainLayout.addLayout(menuLayout, 1)
    
    # game grid
    self.gameGrid, gridLayout = self._createGrid(rows=rows, columns=columns)
    self.mainLayout.addLayout(gridLayout, 1000)
    
    # controls
    self.controls = self._createControls()
    self.mainLayout.addLayout(self.controls, 1)
    
    ###########################################################################
    
    
    # set and display the board
    self.displayNewBoard(board)
    

  def _getCellValue(self, x, y):
    """ Return the value we are currently showing for this game cell """
    
    val = self.gameGrid[x][y].text()
    if val == "":
      return 0
    else:
      return int(val)
  
  def _keyPressed(self, event):
    """ Called when the user presses a key """
  
    key = event.key()
    
    # ignore anything that's not a number 1-9 or delete
    if key not in self.DELETE_KEY_LIST and key not in self.NUMBER_KEY_LIST:
      return
    
    # convert the key pressed to its value (delete is 0)
    if key in self.DELETE_KEY_LIST:
      key = 0
    else:
      key = int(chr(key))
    
    # if we have a selected cell then update it
    if self.selectedCell:
      self.controller.updateBoard(x=self.selectedCell.x,
                                  y=self.selectedCell.y,
                                  value=key)
  
  
    
  
  def _highlightSelectedCell(self, x, y):
    """
    # Highlight the given cell and revert the previously highlighted cell
    # to what it was before
    #  -NOTE: can't use _setCellStyle as this ignores selected cell highlighting
    """
    
    # if cell is already highlighted, we're done
    if self.selectedCell and self.selectedCell.x == x and self.selectedCell.y == y:
      return
    
    # if we already have a selected cell, revert it back to what it was before
    if self.selectedCell:
      #self._setCellStyle(self.selectedCell.x, self.selectedCell.y, self.selectedCell.originalStyle)
      self.gameGrid[self.selectedCell.x][self.selectedCell.y].setStyleSheet(self.selectedCell.originalStyle)

    # register the newly selected cell
    self.selectedCell = GUI.SelectedCell(x, y, self.gameGrid[x][y].styleSheet())

    # highlight the new cell
    self.gameGrid[x][y].setStyleSheet(self.CELL_STYLE_HIGHLIGHTED)
    self._setStatusText("{}x{}".format(x,y))
    #self._setCellStyle(x, y, self.CELL_STYLE_HIGHLIGHTED)


  def _controlClicked(self):
    """ Called whenever a control button is pressed """
    
    genDialog = GeneratorDialog(self.mainWindow)
    genDialog.show()
    genDialog.exec_()
    
    return
    #app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog(self.mainWindow)
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    Dialog.exec_()
    #app.exec_()
    
    return
    
    buttonText = self.sender().text()
    
    # when the <x> button is pressed, call function:
    controlMap = {
      "Reset":        self.controller.resetBoard,
      "Clear Errors": self.controller.clearErrors
    }
    
    # if we have a function for this button, call it
    action = controlMap.get(buttonText, None)
    if action is not None:
      action()
  
  @QtCore.pyqtSlot()
  def _menuClicked(self):
    """ Called whenever a menu item is clicked """
    
    menuText = self.sender().text()
    
    # functino to call for each menu option
    actionMap = {
      "New":         self.controller.newBoard,
      "Save":        lambda: print("Save"),
      "Load":        lambda: print("Load"),
      "Quit":        sys.exit,
      "How to Play": lambda: print("How to Play"),
      "About":       lambda: print("About"),
    }
    
    # call menu function
    action = actionMap.get(menuText, None)
    if action is not None:
      action()
    
  def _createMenuBar(self):
    """ Create the menu bar GUI elements"""
    
    # layout
    menuLayout = QtWidgets.QVBoxLayout()
    menuLayout.setAlignment(QtCore.Qt.AlignTop)
    
    # menu bar itself
    menubar = QtWidgets.QMenuBar()
    menubar.setNativeMenuBar(False)
    menubar.setStyleSheet("padding: 1px;")
    menuLayout.addWidget(menubar)
    
    # file
    fileMenu = menubar.addMenu("File")
    fileMenu.addAction("New",  self._menuClicked)
    fileMenu.addAction("Save", self._menuClicked)
    fileMenu.addAction("Load", self._menuClicked)
    fileMenu.addSeparator()
    fileMenu.addAction("Quit", self._menuClicked)
    
    # help
    helpMenu = menubar.addMenu("Help")
    helpMenu.addAction("How to Play", self._menuClicked)
    helpMenu.addAction("About",       self._menuClicked)
    
    return menuLayout
  
  
  def _createGrid(self, rows, columns):
    """ Create the number grid, composed of individual cells """
    
    # grid layout for grid...
    gridLayout = QtWidgets.QGridLayout()
    gridLayout.setSpacing(0)
    
    # create a grid of rows x columns cells
    grid = {}
    for x in range(rows):
      grid[x] = {}
      for y in range(columns):
        grid[x][y] = self._createCell("", x, y)
        gridLayout.addWidget(grid[x][y], x, y)
        
    return grid, gridLayout
  
  
  def _createCell(self, contents, x, y):
    """ Create an individual grid cell """
    
    # cell is a label
    cell = QtWidgets.QLabel(contents)
    cell.setAlignment(QtCore.Qt.AlignCenter)
    cell.setScaledContents(True)
    cell.setStyleSheet(self.CELL_STYLE_NORMAL)
    
    # font for cell text
    font = QtGui.QFont()
    font.setPointSize(16)
    cell.setFont(font)
    
    # can't "click" labels, so register a click with a mouse event
    cell.mousePressEvent = lambda event: self._highlightSelectedCell(x, y)
    return cell

  
  def _createControls(self):
    """ Create the control buttons at the bottom of the window """
    
    # horizontal layout
    controlsGrid = QtWidgets.QHBoxLayout()
    
    button = QtWidgets.QPushButton("Clear Errors")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button)#, 0, 0)

    button = QtWidgets.QPushButton("Reset")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button)#, 0, 1)

    controlsGrid.insertStretch(2,10)
    
    # get an outside reference to the status text as we will want to
    # update it later
    self.statusText = QtWidgets.QLabel("")
    self.statusText.setStyleSheet("font: 14pt; color: darkgreen; ")
    controlsGrid.addWidget(self.statusText)
    
    return controlsGrid
  
  
  def run(self):
    """ Enter the main loop of the GUI """
    
    self.mainWindow.show()
    sys.exit(self.app.exec_())

  
  def _clearBoard(self):
    """ Clear the board grid and reset any messages or statuses """

    # get the dimensions of the board
    rows, columns = self.board.getValues().shape
    
    # for every cell
    for row in range(rows):
      for col in range(columns):
        
        # set cell colours back to default
        self._setCellStyle(row, col, self.CELL_STYLE_NORMAL)
        
        # clear the cell value
        self._setCellValue(row, col, "")
    
    # clear the status text
    self._setStatusText("")
    
        
  def _setStatusText(self, text):
    self.statusText.setText(text)
  
  def boardComplete(self):
    """ Board is complete """
    
    # display finished message
    self._setStatusText("BOARD COMPLETE!")
    
  
  
  def displayNewBoard(self, board):
    """ Register the new board and display it on the game grid"""
    
    # remember this new board
    self.board = board
    
    # clear any past boards
    self._clearBoard()
    
    # get the values and dimensions of the board
    rows, columns = board.getBoardDimensions()
    
    # set the value for each initial cell
    for row in range(rows):
      for column in range(columns):
        val = board.getCellValue(row, column)
        if val != 0:
          self._setCellValue(row, column, str(val))
          self._setCellStyle(row, column, self.CELL_STYLE_INITIAL)
    
    # highlight the groups
    self.highlightGroups()
    
    
  def updateCell(self, x, y):
    """ Update a single cell and any highlighting that may have changed """
    
    newVal = self.board.getCellValue(x,y)
    
    # if the value hasn't changed then no need to update anything
    if newVal == self._getCellValue(x,y):
      return
    
    # set the value of the cell
    self._setCellValue(x, y, str(newVal))
    
    # update the highlighting
    self.highlightGroups()
  
  
  def _setCellValue(self, x, y, value):
    """ Update the contents of a single cell """
    
    # 0 is blank
    if value == "0": value = ""
    
    self.gameGrid[x][y].setText(value)
  
  def _setCellStyle(self, x, y, style):
    """ Set the style of an individual cell in the game grid """
    
    # if this cell is the currently selected one, then change
    # its recorded "original style", rather than current style
    if self.selectedCell and self.selectedCell.x == x and self.selectedCell.y == y:
      self.selectedCell.originalStyle = style
    else:
      self.gameGrid[x][y].setStyleSheet(style)
    
  
  def highlightGroups(self):
    """ Highlight the valid, invalid and orphan groups """

    validGroups   = self.board.getValidGroups()
    invalidGroups = self.board.getInvalidGroups()
    orphanGroups  = self.board.getOrphanGroups()
    
    # orphan groups
    for num in range(0, 10):
  
      # flatten the list of lists of coords into a single list of coords
      cells = [x[i] for x in orphanGroups.get(num, []) for i in range(len(x))]

      # highlight the un-grouped cell groups based on whether they are initial
      # cells or not
      for cell in cells:
  
        # initial cells are styled differently to normal cells
        if self.board.isInitialCell(*cell):
          self._setCellStyle(*cell, self.TEXT_STYLE_INITIAL + self.CELL_STYLE_INITIAL)
        else:
          self._setCellStyle(*cell, self.TEXT_STYLE_NORMAL + self.CELL_STYLE_NORMAL)
    
    
    # valid groups
    for num in range(1, 10):
    
      # flatten the list of lists of coords into a single list of coords
      cells = [x[i] for x in validGroups.get(num, []) for i in range(len(x))]
      
      # highlight the groups their specific number colour
      cellStyle = self.__getattribute__("CELL_STYLE_{}".format(num))
      for cell in cells:
        
        # initial cells are styled differently to normal cells
        if self.board.isInitialCell(*cell):
          self._setCellStyle(*cell, self.TEXT_STYLE_INITIAL + cellStyle)
        else:
          self._setCellStyle(*cell, self.TEXT_STYLE_NORMAL + cellStyle)
    
    
    # invalid groups
    for num in range(1, 10):
  
      # flatten the list of lists of coords into a single list of coords
      cells = [x[i] for x in invalidGroups.get(num, []) for i in range(len(x))]
      for cell in cells:
        
        # initial cells are styled differently to normal cells
        if self.board.isInitialCell(*cell):
          self._setCellStyle(*cell, self.TEXT_STYLE_INITIAL + self.CELL_STYLE_INVALID)
        else:
          self._setCellStyle(*cell, self.TEXT_STYLE_NORMAL + self.CELL_STYLE_INVALID)

class Ui_Dialog(object):
  
  def setupUi(self, Dialog):
    Dialog.setObjectName("Dialog")
    Dialog.resize(506, 424)
    self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
    self.verticalLayout_2.setObjectName("verticalLayout_2")
    self.verticalLayout = QtWidgets.QVBoxLayout()
    self.verticalLayout.setObjectName("verticalLayout")
    self.horizontalLayout = QtWidgets.QHBoxLayout()
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.textEdit = QtWidgets.QTextEdit(Dialog)
    self.textEdit.setObjectName("textEdit")
    self.horizontalLayout.addWidget(self.textEdit)
    self.label = QtWidgets.QLabel(Dialog)
    self.label.setObjectName("label")
    self.horizontalLayout.addWidget(self.label)
    self.textEdit_2 = QtWidgets.QTextEdit(Dialog)
    self.textEdit_2.setObjectName("textEdit_2")
    self.horizontalLayout.addWidget(self.textEdit_2)
    self.verticalLayout.addLayout(self.horizontalLayout)
    spacerItem = QtWidgets.QSpacerItem(20, 800, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
    self.verticalLayout.addItem(spacerItem)
    self.label_3 = QtWidgets.QLabel(Dialog)
    self.label_3.setText("")
    self.label_3.setObjectName("label_3")
    self.verticalLayout.addWidget(self.label_3)
    self.progressBar = QtWidgets.QProgressBar(Dialog)
    self.progressBar.setProperty("value", 24)
    self.progressBar.setObjectName("progressBar")
    self.verticalLayout.addWidget(self.progressBar)
    self.label_2 = QtWidgets.QLabel(Dialog)
    self.label_2.setObjectName("label_2")
    self.verticalLayout.addWidget(self.label_2)
    self.verticalLayout.setStretch(2, 10000)
    self.verticalLayout_2.addLayout(self.verticalLayout)
  
    _translate = QtCore.QCoreApplication.translate
    Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
    self.label.setText(_translate("Dialog", "TextLabel"))
    self.label_2.setText(_translate("Dialog", "TextLabel"))
    QtCore.QMetaObject.connectSlotsByName(Dialog)

class GeneratorDialog(QtWidgets.QDialog):
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setModal(True)
    
    self.setObjectName("Dialog")
    #self.resize(309, 220)
    self.resize(25, 15)
    
    verticalLayout_3 = QtWidgets.QVBoxLayout(self)
    verticalLayout_3.setObjectName("verticalLayout_3")
    verticalLayout_2 = QtWidgets.QVBoxLayout()
    verticalLayout_2.setObjectName("verticalLayout_2")
    horizontalWidget_2 = QtWidgets.QWidget(self)
    horizontalWidget_2.setObjectName("horizontalWidget_2")
    horizontalLayout_3 = QtWidgets.QHBoxLayout(horizontalWidget_2)
    horizontalLayout_3.setObjectName("horizontalLayout_3")
    horizontalWidget = QtWidgets.QWidget(horizontalWidget_2)
    horizontalWidget.setObjectName("horizontalWidget")
    horizontalLayout = QtWidgets.QHBoxLayout(horizontalWidget)
    horizontalLayout.setObjectName("horizontalLayout")
    spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem)
    lineEdit = QtWidgets.QLineEdit(horizontalWidget)
    lineEdit.setObjectName("lineEdit")
    horizontalLayout.addWidget(lineEdit)
    label = QtWidgets.QLabel(horizontalWidget)
    label.setObjectName("label")
    horizontalLayout.addWidget(label)
    lineEdit_2 = QtWidgets.QLineEdit(horizontalWidget)
    lineEdit_2.setObjectName("lineEdit_2")
    horizontalLayout.addWidget(lineEdit_2)
    spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem1)
    verticalWidget = QtWidgets.QWidget(horizontalWidget)
    verticalWidget.setObjectName("verticalWidget")
    verticalLayout = QtWidgets.QVBoxLayout(verticalWidget)
    verticalLayout.setObjectName("verticalLayout")
    spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
    verticalLayout.addItem(spacerItem2)
    label_4 = QtWidgets.QLabel(verticalWidget)
    label_4.setAlignment(QtCore.Qt.AlignCenter)
    label_4.setObjectName("label_4")
    verticalLayout.addWidget(label_4)
    horizontalLayout_2 = QtWidgets.QHBoxLayout()
    horizontalLayout_2.setObjectName("horizontalLayout_2")
    spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout_2.addItem(spacerItem3)
    label_5 = QtWidgets.QLabel(verticalWidget)
    label_5.setStyleSheet("background: white; border-style: outset; border-width: 1px; border-color: black;")
    label_5.setAlignment(QtCore.Qt.AlignCenter)
    label_5.setObjectName("label_5")
    horizontalLayout_2.addWidget(label_5)
    spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout_2.addItem(spacerItem4)
    verticalLayout.addLayout(horizontalLayout_2)
    horizontalLayout.addWidget(verticalWidget)
    spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout.addItem(spacerItem5)
    horizontalLayout.setStretch(0, 1000)
    horizontalLayout.setStretch(1, 1)
    horizontalLayout.setStretch(2, 1)
    horizontalLayout.setStretch(3, 1)
    horizontalLayout.setStretch(6, 1000)
    horizontalLayout_3.addWidget(horizontalWidget)
    verticalLayout_2.addWidget(horizontalWidget_2)
    spacerItem6 = QtWidgets.QSpacerItem(20, 800, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
    verticalLayout_2.addItem(spacerItem6)
    line_2 = QtWidgets.QFrame(self)
    line_2.setFrameShape(QtWidgets.QFrame.HLine)
    line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
    line_2.setObjectName("line_2")
    verticalLayout_2.addWidget(line_2)
    progressBar = QtWidgets.QProgressBar(self)
    progressBar.setProperty("value", 24)
    progressBar.setObjectName("progressBar")
    verticalLayout_2.addWidget(progressBar)
    label_2 = QtWidgets.QLabel(self)
    label_2.setObjectName("label_2")
    verticalLayout_2.addWidget(label_2)
    horizontalLayout_4 = QtWidgets.QHBoxLayout()
    horizontalLayout_4.setObjectName("horizontalLayout_4")
    spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout_4.addItem(spacerItem7)
    horizontalLayout_6 = QtWidgets.QHBoxLayout()
    horizontalLayout_6.setObjectName("horizontalLayout_6")
    lineEdit_3 = QtWidgets.QLineEdit(self)
    lineEdit_3.setAlignment(QtCore.Qt.AlignCenter)
    lineEdit_3.setObjectName("lineEdit_3")
    horizontalLayout_6.addWidget(lineEdit_3)
    pushButton = QtWidgets.QPushButton(self)
    pushButton.setObjectName("pushButton")
    horizontalLayout_6.addWidget(pushButton)
    horizontalLayout_4.addLayout(horizontalLayout_6)
    horizontalLayout_4.setStretch(0, 1000)
    horizontalLayout_4.setStretch(1, 1)
    verticalLayout_2.addLayout(horizontalLayout_4)
    line = QtWidgets.QFrame(self)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    line.setObjectName("line")
    verticalLayout_2.addWidget(line)
    horizontalLayout_5 = QtWidgets.QHBoxLayout()
    horizontalLayout_5.setObjectName("horizontalLayout_5")
    spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    horizontalLayout_5.addItem(spacerItem8)
    label_6 = QtWidgets.QLabel(self)
    label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
    label_6.setObjectName("label_6")
    horizontalLayout_5.addWidget(label_6)
    horizontalLayout_5.setStretch(0, 1000)
    verticalLayout_2.addLayout(horizontalLayout_5)
    verticalLayout_3.addLayout(verticalLayout_2)
    
    self.setWindowTitle("Board Generator")
    
    #label.setText(_translate("Dialog", "X"))
    label.setText("X")
    
    label_4.setText("In Database")
    label_5.setText("20")
    label_2.setText("Progress: ")
    lineEdit_3.setText("10")
    pushButton.setText("Generate")
    label_6.setText("20s")
    
    label_2.setFocus()
    
