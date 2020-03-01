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
    """ Setup the main window """
    
    QtCore.QObject.__init__(self)
    
    ######################################
    
    defaultCellStyle = "border-style: outset; border-width: 1px;"
    self.CELL_STYLE_NORMAL      = defaultCellStyle + "border-color: black; background: white;"
    self.CELL_STYLE_HIGHLIGHTED = defaultCellStyle + "border-color: yellow; background: yellow;"
    
    self.CELL_STYLE_1 = defaultCellStyle + "border-color: black; background: salmon;"
    self.CELL_STYLE_2 = defaultCellStyle + "border-color: black; background: moccasin;"
    self.CELL_STYLE_3 = defaultCellStyle + "border-color: black; background: coral;"
    self.CELL_STYLE_4 = defaultCellStyle + "border-color: black; background: khaki;"
    self.CELL_STYLE_5 = defaultCellStyle + "border-color: black; background: lightgreen;"
    self.CELL_STYLE_6 = defaultCellStyle + "border-color: black; background: aquamarine;"
    self.CELL_STYLE_7 = defaultCellStyle + "border-color: black; background: paleturquoise;"
    self.CELL_STYLE_8 = defaultCellStyle + "border-color: black; background: lightblue;"
    self.CELL_STYLE_9 = defaultCellStyle + "border-color: black; background: thistle;"
    
    self.CELL_STYLE_INVALID = defaultCellStyle + "border-color: black; background: crimson;"

    ###self.funcCall.connect(self.entryUpdated)
    
    # dictionary of all of the function timers we add
    #self.timers = {}
    
    # dictionary of all of our info widgets
    #self.widgets = {}
    
    #self.currentRow = 0
    
    # =========================================================================
    # GUI
    # =========================================================================
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    self.mainWindow = QtWidgets.QWidget()
    
    # set window size and title
    self.mainWindow.resize(600, 600)
    self.mainWindow.setWindowTitle("Fillomino v0.1")

    self.mainWindow.keyPressEvent = self._keyPressed
    
    #cell.mousePressEvent = lambda event: self._cellClicked(event, x, y)
    
    # use a box layout for the other layouts
    self.mainLayout = QtWidgets.QVBoxLayout()
    self.mainWindow.setLayout(self.mainLayout)
    
    # menu bar
    menuLayout = self._createMenuBar()
    self.mainLayout.addLayout(menuLayout, 1)
    
    # game grid
    self.gameGrid, gridLayout = self._createGrid(rows=20, columns=20)
    self.mainLayout.addLayout(gridLayout, 100)
    
    # controls
    self.controls = self._createControls()
    self.mainLayout.addLayout(self.controls, 1)
    # =========================================================================
    
    self.selectedCell = None
    #self.currentCell = None

    self.controller = controller
    self.board      = board
    
    # set and display the board
    self.setBoard(board)
    
  
  def _keyPressed(self, event):
    
    # ignore anything that's not a number 1-9
    key = event.key()
    if key < 49 or key > 57:
      return
    
    # if we have a selected cell then update it
    if self.selectedCell:
      self.controller.updateBoard(x=self.selectedCell.x,
                                  y=self.selectedCell.y,
                                  value=chr(key))
    
    ## set the current cell to this number
    #if self.currentCell:
    #  self.currentCell.setText(chr(key))
  
  
    
  
  def _highlightCell(self, x, y):
    """
    # Highlight the given cell and return the previously highlighted cell
    # to what it was before
    """
    
    # if cell is already highlighted, we're done
    if self.selectedCell and self.selectedCell.x == x and self.selectedCell.y == y:
      return
    
    # if we already have a selected cell, revert it back to what it was before
    if self.selectedCell:
      self._setCellStyle(self.selectedCell.x, self.selectedCell.y, self.selectedCell.originalStyle)
      #self.gameGrid[self.selectedCell.x][self.selectedCell.y]\
      #  .setStyleSheet(self.selectedCell.originalStyle)

    # register the newly selected cell
    self.selectedCell = GUI.SelectedCell(x, y, self.gameGrid[x][y].styleSheet())

    # highlight the new cell
    #self.gameGrid[x][y].setStyleSheet(self.CELL_STYLE_HIGHLIGHTED)
    self._setCellStyle(x, y, self.CELL_STYLE_HIGHLIGHTED)

  def DEP_cellClicked(self, event, x, y):
    """ Called whenever a cell is clicked """
    
    # if we already have a selected cell, and the new cell is different, return
    # the previously selected cell back to what it was before
    if self.selectedCell and self.selectedCell.x != x and self.selectedCell.y != y:
      self._highlightCell(self.selectedCell.x, self.selectedCell.y, self.selectedCell.originalStyle)
      
    # register the newly selected cell
    self.selectedCell = GUI.SelectedCell(x,y,self.gameGrid[x][y].styleSheet())
    
    # highlight the new cell
    self._highlightCell(x, y, self.CELL_STYLE_HIGHLIGHTED)
    
    """
    # set the current cell to normal
    if self.currentCellCoords:
      #self.currentCell.setStyleSheet(GUI.CELL_STYLE_NORMAL)
      self._highlightCell(*self.currentCellCoords, GUI.CELL_STYLE_NORMAL)
      
    # make this cell the current cell
    self.currentCellCoords = (x, y)
    self._highlightCell(*self.currentCellCoords, GUI.CELL_STYLE_HIGHLIGHTED)
    #self.currentCell = self.gameGrid[x][y]
    #self.gameGrid[x][y].setStyleSheet(GUI.CELL_STYLE_HIGHLIGHTED)
    """

  def _controlClicked(self):
    """ Called whenever a control button is pressed """

    controlAction = self.sender()
    
    controlMap = {
      "Reset": self.controller.resetBoard,
      "Clear Errors": self.controller.clearErrors
    }
    
    action = controlMap.get(controlAction.text(), None)
    if action is not None:
      action()
  
  @QtCore.pyqtSlot()
  def _menuClicked(self):
    """ Called whenever a menu item is clicked """
    
    menuAction = self.sender()
    
    actionMap = {
      "New":   self.controller.newBoard,
      "Save":  lambda: print("Save"),
      "Load":  lambda: print("Load"),
      "Quit":  sys.exit,
      "About": lambda: print("About"),
    }
    
    action = actionMap.get(menuAction.text(), None)
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
    helpMenu.addAction("About",  self._menuClicked)
    
    return menuLayout
  
  
  def _createGrid(self, rows, columns):
    """ Create the number grid, composed of individual cells """
    
    gridLayout = QtWidgets.QGridLayout()
    gridLayout.setSpacing(0)
  
    #options = [""] + [str(x) for x in range(1, 10)]
  
    grid = {}
    for x in range(rows):
      grid[x] = {}
      for y in range(columns):
        #grid[x][y] = self._createCell(np.random.choice(options), x, y)
        grid[x][y] = self._createCell("", x, y)
        gridLayout.addWidget(grid[x][y], x, y)
        
    return grid, gridLayout
  

  #@staticmethod
  def _createCell(self, contents, x, y):
    """ Create an individual grid cell """

    cell = QtWidgets.QLabel(contents)
    cell.setAlignment(QtCore.Qt.AlignCenter)
    cell.setScaledContents(True)
    # cell.setStyleSheet("margin-left: 10px; border-radius: 25px; background: white; color: #4A0C46;")
    cell.setStyleSheet(self.CELL_STYLE_NORMAL)#"border-style: outset; border-width: 1px; border-color: black; background: white;")
    
    font = QtGui.QFont()
    #font.setFamily("FreeMono")
    font.setPointSize(14)
    cell.setFont(font)
    
    # can't click labels...
    #cell.mousePressEvent = lambda event: self._cellClicked(event, x, y)
    #cell.clicked.connect(lambda event: self._cellClicked(event, x, y))
    cell.mousePressEvent = lambda event: self._highlightCell(x, y)
    return cell

  
  def _createControls(self):
    """ Create the control buttons at the bottom of the window """
  
    controlsGrid = QtWidgets.QGridLayout()
    controlsGrid.setAlignment(QtCore.Qt.AlignLeft)
    
    button = QtWidgets.QPushButton("Clear Errors")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button, 0, 0)

    button = QtWidgets.QPushButton("Reset")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button, 0, 1)

    return controlsGrid
  
  # display the gui
  def run(self):
    """ Enter the main loop of the GUI """
    self.mainWindow.show()
    sys.exit(self.app.exec_())

  
  def _clearBoard(self):
    """  """

    # get the dimensions of the board
    rows, columns = self.board.getValues().shape
    
    # for every cell
    for row in range(rows):
      for col in range(columns):
        
        # set cell colours back to default
        self._setCellStyle(row, col, self.CELL_STYLE_NORMAL)
        
        # clear its value
        self.updateCell(row, col, "")
        
  
  def setBoard(self, board):
    """ Store the board and display it """
    
    # clear any past boards
    self._clearBoard()
    
    # remember this new board
    self.board = board
    
    # get the values and dimensions of the board
    vals = board.getValues()
    rows, columns = vals.shape
    
    # set the value for each cell
    for row in range(rows):
      for column in range(columns):
        val = vals[row][column]
        
        # make 0 an empty string
        if val == 0: val = ""
        else:        val = str(val)
        
        #self.gameGrid[row][column].setText(val)
        self.updateCell(row, column, val)
  
  def updateCell(self, x, y, value):
    """ Update the contents of a single cell"""
    self.gameGrid[x][y].setText(value)
  
  
  def _setCellStyle(self, x, y, style):
    self.gameGrid[x][y].setStyleSheet(style)
    
  
  def highlightValidGroups(self, validGroups):
    """ Highlight the valid groups according to their number """
    
    for num in range(1,10):
      
      # flatten the list of lists of coords into a single list of coords
      cells  = [x[i] for x in validGroups.get(num, []) for i in range(len(x))]
      colour = self.__getattribute__("CELL_STYLE_{}".format(num))
      
      for cell in cells:
        self._setCellStyle(*cell, colour)
        
  def highlightInvalidGroups(self, validGroups):
    """ Highlight invalid groups """
    
    for num in range(1, 10):
    
      # flatten the list of lists of coords into a single list of coords
      cells = [x[i] for x in validGroups.get(num, []) for i in range(len(x))]
      for cell in cells:
        self._setCellStyle(*cell, self.CELL_STYLE_INVALID)
  
  