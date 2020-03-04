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
    
    #############################
    
    # backspace and delete
    self.DELETE_KEY_LIST = [16777219, 16777223]
    
    # 1 to 9
    self.NUMBER_KEY_LIST = list(range(49, 58))
    
    # 87: w
    # 65: a
    # 83: s
    # 68: d
    
    ################
    
    
    
    # =========================================================================
    # GUI
    # =========================================================================
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    self.mainWindow = QtWidgets.QWidget()
    
    # set window size and title
    self.mainWindow.resize(700, 700)
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
    rows, columns = board.getBoardDimensions()
    self.gameGrid, gridLayout = self._createGrid(rows=rows, columns=columns)
    self.mainLayout.addLayout(gridLayout, 100)
    
    # controls
    self.controls = self._createControls()
    self.mainLayout.addLayout(self.controls, 1)
    # =========================================================================
    
    self.selectedCell = None
    

    self.controller = controller
    self.board      = None
    
    # set and display the board
    self.displayNewBoard(board)

  def _getCellValue(self, x, y):
    val = self.gameGrid[x][y].text()
    if val == "":
      return 0
    else:
      return int(val)
  
  def _keyPressed(self, event):
  
    key = event.key()
    
    # ignore anything that's not a number 1-9 or delete
    if key not in self.DELETE_KEY_LIST and key not in self.NUMBER_KEY_LIST:
      return
    
    # convert the key pressed to its value (delete is 0)
    if key in self.DELETE_KEY_LIST:
      key = "0"
    else:
      key = chr(key)
    
    # if we have a selected cell then update it
    if self.selectedCell:
      self.controller.updateBoard(x=self.selectedCell.x,
                                  y=self.selectedCell.y,
                                  value=key)
    
    ## set the current cell to this number
    #if self.currentCell:
    #  self.currentCell.setText(chr(key))
  
  
    
  
  def _highlightSelectedCell(self, x, y):
    """
    # Highlight the given cell and return the previously highlighted cell
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

  def DEP_cellClicked(self, event, x, y):
    """ Called whenever a cell is clicked """
    
    # if we already have a selected cell, and the new cell is different, return
    # the previously selected cell back to what it was before
    if self.selectedCell and self.selectedCell.x != x and self.selectedCell.y != y:
      self._highlightSelectedCell(self.selectedCell.x, self.selectedCell.y, self.selectedCell.originalStyle)
      
    # register the newly selected cell
    self.selectedCell = GUI.SelectedCell(x,y,self.gameGrid[x][y].styleSheet())
    
    # highlight the new cell
    self._highlightSelectedCell(x, y, self.CELL_STYLE_HIGHLIGHTED)
    
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
    font.setPointSize(16)
    cell.setFont(font)
    
    # can't click labels...
    #cell.mousePressEvent = lambda event: self._cellClicked(event, x, y)
    #cell.clicked.connect(lambda event: self._cellClicked(event, x, y))
    cell.mousePressEvent = lambda event: self._highlightSelectedCell(x, y)
    return cell

  
  def _createControls(self):
    """ Create the control buttons at the bottom of the window """
  
    controlsGrid = QtWidgets.QHBoxLayout()# QGridLayout()
    #controlsGrid.setAlignment(QtCore.Qt.AlignLeft)
    
    button = QtWidgets.QPushButton("Clear Errors")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button)#, 0, 0)

    button = QtWidgets.QPushButton("Reset")
    button.clicked.connect(self._controlClicked)
    controlsGrid.addWidget(button)#, 0, 1)

    controlsGrid.insertStretch(2,10)
    
    self.statusText = QtWidgets.QLabel("")
    self.statusText.setStyleSheet("font: 14pt; color: darkgreen; ")
    controlsGrid.addWidget(self.statusText)#, 0, 100)
    
    return controlsGrid
  
  # display the gui
  def run(self):
    """ Enter the main loop of the GUI """
    self.mainWindow.show()
    sys.exit(self.app.exec_())

  
  def _clearBoard(self):
    """ Clear the board and reset any messages or statuses """

    # get the dimensions of the board
    rows, columns = self.board.getValues().shape
    
    # for every cell
    for row in range(rows):
      for col in range(columns):
        
        # set cell colours back to default
        self._setCellStyle(row, col, self.CELL_STYLE_NORMAL)
        
        # clear its value
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
    """ Store the board and display it """
    
    # remember this new board
    self.board = board
    
    # clear any past boards
    self._clearBoard()
    
    # get the values and dimensions of the board
    vals = board.getValues()
    rows, columns = vals.shape
    
    # set the value for each cell
    for row in range(rows):
      for column in range(columns):
        val = vals[row][column]
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
    
    # if this cell is the currently selected one then change
    # its recorded "original style", rather than current style
    if self.selectedCell and self.selectedCell.x == x and self.selectedCell.y == y:
      self.selectedCell.originalStyle = style
    else:
      self.gameGrid[x][y].setStyleSheet(style)
    
  
  def highlightGroups(self):#, validGroups, invalidGroups, orphanGroups):
    """ Highlight the valid, invalid and orphan groups """

    validGroups   = self.board.getValidGroups()
    invalidGroups = self.board.getInvalidGroups()
    orphanGroups  = self.board.getOrphanGroups()
    
    # orphan groups
    for num in range(0, 10):
  
      # flatten the list of lists of coords into a single list of coords
      cells = [x[i] for x in orphanGroups.get(num, []) for i in range(len(x))]
      #cells = orphanGroups.get(num, [])

      # highlight the un-grouped cell groups their specific number colour
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
        
        
