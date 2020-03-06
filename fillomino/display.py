import datetime
import logging
import threading
import time

logger = logging.getLogger(__name__)

import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

import numpy as np

import PyQt5.QtWidgets as QtWidgets

class GUI(object):
  
  def run(self):
    """ Start GUI """
    raise NotImplementedError("subclass must implement")
  
  def addedNewBoards(self):
    """ Called when new boards are available in the database """
    raise NotImplementedError("subclass must implement")
  
  def boardComplete(self):
    """ Called when board is completed """
    raise NotImplementedError("subclass must implement")
  
  def displayNewBoard(self, board):
    """ Register the new board and display it """
    raise NotImplementedError("subclass must implement")
  
  def notifyStatus(self, text):
    """ Status notification; used or ignored, up to the GUI """
    raise NotImplementedError("subclass must implement")
  
  def updateCell(self, row, column):
    """ Called when the given board cell is updated """
    raise NotImplementedError("subclass must implement")

class PyQtGUI(GUI, QtCore.QObject):
  """
  """

  def notifyStatus(self, text):
    pass

  #CELL_STYLE_NORMAL      = "border-style: outset; border-width: 1px; border-color: black; background: white;"
  #CELL_STYLE_HIGHLIGHTED = "border-style: outset; border-width: 1px; border-color: yellow; background: yellow;"
  
  class SelectedCell(object):
    def __init__(self, x, y, originalStyle):
      self.x = x
      self.y = y
      self.originalStyle = originalStyle

  class BoardGeneratorDialog(QtWidgets.QDialog):
    

    
    class UserActions(object):
      
      @staticmethod
      def generateButtonPressed(dialog, gui):
        """ """
        
        startGenerationMsg = "Generate"
        stopGenerationMsg  = "Stop"
        
        
        buttonText = dialog.sender().text()
        
        # if the user wants to stop an ongoing generation
        if buttonText == stopGenerationMsg:
          gui.controller.stopGeneration = True
          return
        
        # CHECK: row choice is valid
        rows = dialog.getRowChoice()
        if not rows.isdigit():
          dialog.setStatus("Rows must be a number")
          return

        # CHECK: column choice is valid
        columns = dialog.getColumnChoice()
        if not columns.isdigit():
          dialog.setStatus("Columns must be a number")
          return

        # CHECK: number of boards choice is valid
        numBoards = dialog.getNumBoardsChoice()
        if not numBoards.isdigit():
          dialog.notifyStatus("Number of boards must be a number")
          return
        elif not (0 < int(numBoards) < 1000):
          dialog.notifyStatus("Number of boards must be 1-999")
          return

        # set the button text to the stop message
        dialog.setGenerateButtonText(stopGenerationMsg)
        
        # generate the boards
        dialog.setStatus("Generating...")
        dialog.setProgress(0)
        
        # thread to update the status and progress bar
        global killThread
        killThread = False
        def updateStatus():
          
          while True:
            
            # display the progress
            progress = gui.controller.getBoardGenerationProgress()
            dialog.setStatus(gui.controller.getBoardGenerationStatus())
            dialog.setProgress(progress*100)
            
            # exit if we get the kill signal
            if killThread:
              return
            
            time.sleep(0.5)
        
        # create the monitoring thread and start board generation
        monitorThread = threading.Thread(target=updateStatus)
        monitorThread.start()
        
        def genBoards():
  
          global killThread
          
          gui.controller.generateBoards(int(numBoards), int(rows), int(columns))
          
          # send the signal to kill the monitor thread and wait for it to exit
          killThread = True
          monitorThread.join()
          
          # revert the button text to the start message
          dialog.setGenerateButtonText(startGenerationMsg)
          
          # update the database board count and notify the main window that
          # we added new boards
          dialog.updateDatabaseCount()
          gui.addedNewBoards()
        
        generatorThread = threading.Thread(target=genBoards)
        generatorThread.start()
    
    def __init__(self, parent, gui):
      super().__init__(parent)
    
      # reference to our parent gui
      self.gui = gui
    
      self.setWindowTitle("Board Generator")
      self.resize(1, 1)
    
      self.setModal(True)
      self.setObjectName("Dialog")
    
      verticalLayout_3 = QtWidgets.QVBoxLayout(self)
      verticalLayout_2 = QtWidgets.QVBoxLayout()
      horizontalWidget_2 = QtWidgets.QWidget(self)
      horizontalLayout_3 = QtWidgets.QHBoxLayout(horizontalWidget_2)
      horizontalWidget = QtWidgets.QWidget(horizontalWidget_2)
      horizontalLayout = QtWidgets.QHBoxLayout(horizontalWidget)
      spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem)
      
      self.rowsLabel = QtWidgets.QLineEdit(horizontalWidget)
      self.rowsLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      horizontalLayout.addWidget(self.rowsLabel)
      
      label = QtWidgets.QLabel(horizontalWidget)

      horizontalLayout.addWidget(label)
      
      self.columnsLabel = QtWidgets.QLineEdit(horizontalWidget)
      self.columnsLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      horizontalLayout.addWidget(self.columnsLabel)
      
      spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem1)
      verticalWidget = QtWidgets.QWidget(horizontalWidget)

      verticalLayout = QtWidgets.QVBoxLayout(verticalWidget)
      spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
      verticalLayout.addItem(spacerItem2)
      
      label_4 = QtWidgets.QLabel(verticalWidget)
      label_4.setAlignment(QtCore.Qt.AlignCenter)
      verticalLayout.addWidget(label_4)
      
      horizontalLayout_2 = QtWidgets.QHBoxLayout()
      spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_2.addItem(spacerItem3)
      
      self.inDatabaseLabel = QtWidgets.QLabel(verticalWidget)
      self.inDatabaseLabel.setStyleSheet("background: white; border-style: outset; border-width: 3px; border-color: black;")
      self.inDatabaseLabel.setAlignment(QtCore.Qt.AlignCenter)
      horizontalLayout_2.addWidget(self.inDatabaseLabel)
      
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
      verticalLayout_2.addWidget(line_2)
      
      self.progressBar = QtWidgets.QProgressBar(self)
      self.progressBar.setProperty("value", 0)
      verticalLayout_2.addWidget(self.progressBar)
      
      self.statusLabel = QtWidgets.QLabel(self)
      verticalLayout_2.addWidget(self.statusLabel)
      
      horizontalLayout_4 = QtWidgets.QHBoxLayout()
      spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_4.addItem(spacerItem7)
      horizontalLayout_6 = QtWidgets.QHBoxLayout()
      
      
      self.toGenerateLabel = QtWidgets.QLineEdit(self)
      self.toGenerateLabel.setAlignment(QtCore.Qt.AlignCenter)
      horizontalLayout_6.addWidget(self.toGenerateLabel)
      
      
      
      self.generateButton = QtWidgets.QPushButton(self)
      horizontalLayout_6.addWidget(self.generateButton)
      self.generateButton.clicked.connect(
        lambda: PyQtGUI.BoardGeneratorDialog.UserActions.generateButtonPressed(self, self.gui))
      
      horizontalLayout_4.addLayout(horizontalLayout_6)
      horizontalLayout_4.setStretch(0, 1000)
      horizontalLayout_4.setStretch(1, 1)
      verticalLayout_2.addLayout(horizontalLayout_4)
      line = QtWidgets.QFrame(self)
      line.setFrameShape(QtWidgets.QFrame.HLine)
      line.setFrameShadow(QtWidgets.QFrame.Sunken)
      verticalLayout_2.addWidget(line)
      horizontalLayout_5 = QtWidgets.QHBoxLayout()
      spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_5.addItem(spacerItem8)
      
      self.timeElapsedLabel = QtWidgets.QLabel(self)
      self.timeElapsedLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
      horizontalLayout_5.addWidget(self.timeElapsedLabel)
      
      horizontalLayout_5.setStretch(0, 1000)
      verticalLayout_2.addLayout(horizontalLayout_5)
      verticalLayout_3.addLayout(verticalLayout_2)

      label_4.setText("In Database")
      label.setText("X")
      
      # set row and column labels to the current board dimensions
      self.rowsLabel.setText(str(gui.board.getBoardDimensions()[0]))
      self.columnsLabel.setText(str(gui.board.getBoardDimensions()[1]))

      # when the row/column choice is updated, update the "in database" label
      self.rowsLabel.textChanged.connect(self.updateDatabaseCount)
      self.columnsLabel.textChanged.connect(self.updateDatabaseCount)
      
      # default values for labels
      self.inDatabaseLabel.setText(" 0 ")
      self.toGenerateLabel.setText("10")
      self.timeElapsedLabel.setText("")
      self.statusLabel.setText("")
      
      # generate button
      self.generateButton.setText("Generate")
      self.generateButton.setFocus()
      
      # update the "in database" label
      self.updateDatabaseCount()
      
      # keep track of whether we are generating boards now
      self.generatingBoards = False
    
    def updateDatabaseCount(self):
      """ Update the status showing the number of row x colum boards we have in the database """
      
      try:
  
        # get the rows and columns
        rows    = int(self.getRowChoice())
        columns = int(self.getColumnChoice())
        
        # find the board info for this board type
        boardsInfo = self.gui.controller.getBoardsInfo()
        if boardsInfo and boardsInfo.get((rows, columns), False):
          self.setInDatabaseStatus(boardsInfo[(rows, columns)]["length"])
        else:
          self.setInDatabaseStatus(0)
          
      except:
        self.setInDatabaseStatus(0)
      
    def setProgress(self, val):
      self.progressBar.setValue(val)
      
    def setStatus(self, text):
      self.statusLabel.setText(text)
    
    def getRowChoice(self):
      return self.rowsLabel.text()
    
    def getColumnChoice(self):
      return self.columnsLabel.text()
    
    def getNumBoardsChoice(self):
      return self.toGenerateLabel.text()
    
    def setInDatabaseStatus(self, value):
      if isinstance(value, int):
        self.inDatabaseLabel.setText(" " + str(value) + " ")
    
    def setGenerateButtonText(self, text):
      self.generateButton.setText(text)
    
  class UserActions(object):
    
    @staticmethod
    def cellClick(gui, coordinates):
      """ When a user clicks on the cell at <coordinates> """
      gui.highlightSelectedCell(*coordinates)

    @staticmethod
    def controlButton(gui):
      """ Called whenever a control button is pressed """
      
      name = gui.sender().text()
  
      # when the <x> button is pressed, call function:
      controlMap = {
        "Reset":        gui.controller.resetBoard,
        "Clear Errors": gui.controller.clearErrors
      }
  
      # if we have a function for this button, call it
      action = controlMap.get(name, None)
      if action is not None:
        action()
    
    
    @staticmethod
    def keyPressed(gui, event):
      """ Called when the user presses a key """
  
      key = event.key()
  
      # ignore anything that's not a number 1-9 or delete
      if key not in gui.DELETE_KEY_LIST and key not in gui.NUMBER_KEY_LIST:
        return
  
      # convert the key pressed to its value (delete is 0)
      if key in gui.DELETE_KEY_LIST:
        key = 0
      else:
        key = int(chr(key))
  
      # if we have a selected cell then update it
      if gui.selectedCell:
        gui.controller.updateBoard(x=gui.selectedCell.x,
                                   y=gui.selectedCell.y,
                                   value=key)
    
    @staticmethod
    def menuFile(gui):
      """ Called whenever a file menu item is clicked """
      
      name = gui.sender().text()
      
      # function to call for each menu option
      actionMap = {
        "Load Random Board":  gui.controller.loadRandomBoard,
        "Quit": sys.exit
      }
  
      # call menu function
      action = actionMap.get(name, None)
      if action is not None:
        action()
    
    
    @staticmethod
    def menuBoard(gui):
      """ Called whenever a board menu item is clicked """

      name = gui.sender().text()
      
      # function to call for each menu option
      actionMap = {
        "Generate New Boards": gui.showBoardGeneratorWindow,
      }
      
      # call menu function
      action = actionMap.get(name, None)
  
      # clicked on a board dimension option, so set the dimensions
      if action is None:
        rows, cols = map(int, name.split("\t")[0].split("x"))
        gui.controller.setBoardDimensions(rows, cols)
  
      # mapped to an action above
      else:
        action()
    
    @staticmethod
    def menuHelp(gui):
      """ Called whenever a help menu item is clicked """
  
      name = gui.sender().text()
  
      # function to call for each menu option
      actionMap = {
        "How to Play": lambda: print("How to Play"),
        "About":       lambda: print("About"),
      }
  
      # call menu function
      action = actionMap.get(name, None)
      if action is not None:
        action()
  
  
  class LayoutCreator(object):
    
    def __init__(self, gui, mainWindow):
      
      self.gui        = gui
      self.mainWindow = mainWindow

      self.mainWindow.move(0, 0)
      
      # use a box layout for the other layouts
      self.mainLayout = QtWidgets.QVBoxLayout()
      self.mainWindow.setLayout(self.mainLayout)
      
      # GUI elements we want to be able to update
      self.gameGrid   = None
      self.statusText = None
    
    #def setGameGridCell(self, row, column, value):
    #  self.gameGrid[row][column].setText(value)
    
    def getGameGrid(self):
      return self.gameGrid
    
    def setStatusText(self, text):
      if self.statusText:
        self.statusText.setText(text)
    
    
    def _delLayout(self, layout=None):
      """ Delete all of the layout elements """
      
      if layout is None:
        layout = self.mainLayout
      
      while layout.count():
        child  = layout.takeAt(0)
        widget = child.widget()
        
        if widget:
          layout.removeWidget(widget)
          widget.deleteLater()
        
        else:
          try:
            if child.count():
              self._delLayout(child)
              child.deleteLater()
          except: pass
        

      
      #for i in reversed(range(self.mainLayout.count())):
      #  self.mainLayout.itemAt(i).setParent(None)
      
      # remove any previous gui elements
      #while self.mainLayout.count() > 0:
      #  self.mainLayout.takeAt(0)
    
    def setlayout(self, rows, columns):
      
      # remove any previous gui elements
      self._delLayout()
  
      # menu bar
      menuLayout = self.createMenuBar()
      self.mainLayout.insertLayout(0, menuLayout, 1)
  
      # game grid
      self.gameGrid, gridLayout = self.createGrid(rows=rows, columns=columns)
      self.mainLayout.insertLayout(1, gridLayout, 1000)
      
      # controls
      controls = self.createControls()
      self.mainLayout.insertLayout(2, controls, 1)
      
      # set window size
      self.mainWindow.resize(35 * rows, 35 * columns)
    
    def updateMenuBar(self):
      """ If our board info has changed, update the menu bar items """
      
      # remove the old menu bar
      self.mainLayout.takeAt(0)
      
      # insert a newly updated menu bar
      self.mainLayout.insertLayout(0, self.createMenuBar(), 1)
      
      
    def createMenuBar(self):
      """ Create the menu bar GUI elements"""
    
      # layout
      menuLayout = QtWidgets.QVBoxLayout()
      menuLayout.setAlignment(QtCore.Qt.AlignTop)
    
      # menu bar itself
      menubar = QtWidgets.QMenuBar()
      menubar.setNativeMenuBar(False)
      menubar.setStyleSheet("padding: 1px;")
      menuLayout.addWidget(menubar)
    
      ###########################################################################
      # file
      ###########################################################################
    
      fileMenu = menubar.addMenu("File")
      fileMenu.addAction("Load Random Board", lambda: PyQtGUI.UserActions.menuFile(self.gui))
      fileMenu.addSeparator()
      fileMenu.addAction("Quit", lambda: PyQtGUI.UserActions.menuFile(self.gui))
    
      ###########################################################################
      # boards
      ###########################################################################
    
      boardInfo = self.gui.controller.getBoardsInfo()
      boardDims = self.gui.board.getBoardDimensions()
    
      fileMenu = menubar.addMenu("Boards")
    
      # add a board option for each type of board in the database
      if len(boardInfo) == 0:
        fileMenu.addAction("<No Boards Found>")
    
      else:
      
        # each board option will give the dimensions and show the number
        # of those board types we have in the database
        for (rows, cols), info in boardInfo.items():
          optionText = "{}x{}\t({})".format(rows, cols, info["length"])
          action = QtWidgets.QAction(optionText, self.mainWindow)
          action.triggered.connect(lambda: PyQtGUI.UserActions.menuBoard(self.gui))
          action.setCheckable(True)
          fileMenu.addAction(action)
        
          # tick this option if it's our current board's dimensions
          if (rows, cols) == boardDims:
            action.setChecked(True)
    
      fileMenu.addSeparator()
      fileMenu.addAction("Generate New Boards", lambda: PyQtGUI.UserActions.menuBoard(self.gui))
    
      ###########################################################################
      # help
      ###########################################################################
    
      helpMenu = menubar.addMenu("Help")
      helpMenu.addAction("How to Play", lambda: PyQtGUI.UserActions.menuHelp(self.gui))
      helpMenu.addAction("About",       lambda: PyQtGUI.UserActions.menuHelp(self.gui))
    
      return menuLayout
  
  
    def createGrid(self, rows, columns):
      """ Create the number grid, composed of individual cells """
    
      # grid layout for grid...
      gridLayout = QtWidgets.QGridLayout()
      gridLayout.setSpacing(0)
    
      # create a grid of rows x columns cells
      grid = {}
      for x in range(rows):
        grid[x] = {}
        for y in range(columns):
          grid[x][y] = self.createCell("", x, y)
          gridLayout.addWidget(grid[x][y], x, y)
    
      return grid, gridLayout
  
  
    def createCell(self, contents, x, y):
      """ Create an individual grid cell """
    
      # cell is a label
      cell = QtWidgets.QLabel(contents)
      cell.setAlignment(QtCore.Qt.AlignCenter)
      cell.setScaledContents(True)
      cell.setStyleSheet(self.gui.CELL_STYLE_NORMAL)
    
      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(16)
      cell.setFont(font)
    
      # can't "click" labels, so register a click with a mouse event
      cell.mousePressEvent = lambda event: PyQtGUI.UserActions.cellClick(self.gui, (x, y))
      return cell
    
    
    def createControls(self):
      """ Create the control buttons at the bottom of the window """
    
      # horizontal layout
      controlsGrid = QtWidgets.QHBoxLayout()
      
      # add buttons
      for buttonText in ["Clear Errors", "Reset"]:
        button = QtWidgets.QPushButton(buttonText)
        button.clicked.connect(lambda: PyQtGUI.UserActions.controlButton(self.gui))
        controlsGrid.addWidget(button)
    
      controlsGrid.insertStretch(2, 10)
    
      # get an outside reference to the status text as we will want to
      # update it later
      self.statusText = QtWidgets.QLabel("")
      self.statusText.setStyleSheet("font: 12pt; color: darkgreen; ")
      controlsGrid.addWidget(self.statusText)
    
      return controlsGrid

  # initial setup
  def __init__(self, controller, board):
    """ GUI initialisation """
    
    super().__init__()
    
    # references to controller and the board to display
    self.controller = controller
    self.board      = board
    
    # highlighted/selected cell
    self.selectedCell = None
    
    # gui representation of the board
    #self.gameGrid = None
    
    # get board dimensions
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
    self.CELL_STYLE_2 = defaultCellStyle+"background: bisque;"
    self.CELL_STYLE_3 = defaultCellStyle+"background: khaki;"
    self.CELL_STYLE_4 = defaultCellStyle+"background: lightskyblue;"
    self.CELL_STYLE_5 = defaultCellStyle+"background: aquamarine;"
    self.CELL_STYLE_6 = defaultCellStyle+"background: thistle;"
    self.CELL_STYLE_7 = defaultCellStyle+"background: palegoldenrod;"
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
    self.mainWindow.setWindowTitle("Fillomino v0.1")
    
    # register function for keyboard presses
    self.mainWindow.keyPressEvent = lambda event: PyQtGUI.UserActions.keyPressed(self, event)
    
    self.appCreator = PyQtGUI.LayoutCreator(self, self.mainWindow)
    self.appCreator.setlayout(rows, columns)
    
    # get links into elements we want to be able to change
    self._getGameGrid   = self.appCreator.getGameGrid
    self._setStatusText = self.appCreator.setStatusText

    self.notifyStatus = self.appCreator.setStatusText
    
    ###########################################################################
    
    
    # set and display the board
    self.displayNewBoard(board)
    

  def _getCellValue(self, x, y):
    """ Return the value we are currently showing for this game cell """
    
    val = self._getGameGrid()[x][y].text()
    if val == "":
      return 0
    else:
      return int(val)

  def _setCellValue(self, x, y, value):
    """ Update the contents of a single cell """
  
    # 0 is blank
    if value == "0": value = ""
  
    self._getGameGrid()[x][y].setText(value)

  def _setCellStyle(self, x, y, style):
    """ Set the style of an individual cell in the game grid """
  
    # if this cell is the currently selected one, then change
    # its recorded "original style", rather than current style
    if self.selectedCell and self.selectedCell.x == x and self.selectedCell.y == y:
      self.selectedCell.originalStyle = style
    else:
      self._getGameGrid()[x][y].setStyleSheet(style)


  def _clearBoard(self):
    """ Clear the board grid and reset any messages or statuses """
  
    # get the dimensions of the board
    rows, columns = self.board.getBoardDimensions()
  
    # for every cell
    for row in range(rows):
      for col in range(columns):
        # set cell colours back to default
        self._setCellStyle(row, col, self.CELL_STYLE_NORMAL)
      
        # clear the cell value
        self._setCellValue(row, col, "")
  
    # clear the status text
    self._setStatusText("")


  def _highlightGroups(self):
    """ Highlight the valid, invalid and orphan groups """
  
    validGroups = self.board.getValidGroups()
    invalidGroups = self.board.getInvalidGroups()
    orphanGroups = self.board.getOrphanGroups()
  
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




  
  def run(self):
    """ Enter the main loop of the GUI """
    
    self.mainWindow.show()
    sys.exit(self.app.exec_())

  

  def addedNewBoards(self):
    """ Called when new boards are available in the database """
    self.appCreator.updateMenuBar()
  
  def boardComplete(self):
    """ Board is complete """
    
    # display finished message
    self._setStatusText("BOARD COMPLETE!")
    
  
  
  def displayNewBoard(self, board):
    """ Register the new board and display it on the game grid"""
    
    # dimensions of the old board
    oldRows, oldColumns = self.board.getBoardDimensions()

    # dimensions of the new board
    rows, columns = board.getBoardDimensions()
    
    # remember this new board
    self.board = board
    
    # if this board has different dimensions to our current one, update
    # the app layout to accommodate the new size
    if (rows, columns) != (oldRows, oldColumns ):
      self.appCreator.setlayout(rows, columns)
      #self._setupAppLayout(rows, columns)
    
    # clear any past boards
    self._clearBoard()
    
    # set the value for each initial cell
    for row in range(rows):
      for column in range(columns):
        val = board.getCellValue(row, column)
        if val != 0:
          self._setCellValue(row, column, str(val))
          self._setCellStyle(row, column, self.CELL_STYLE_INITIAL)
    
    # highlight the groups
    self._highlightGroups()
    
    
  def updateCell(self, x, y):
    """ Update a single cell and any highlighting that may have changed """
    
    newVal = self.board.getCellValue(x,y)
    
    # if the value hasn't changed then no need to update anything
    if newVal == self._getCellValue(x,y):
      return
    
    # set the value of the cell
    self._setCellValue(x, y, str(newVal))
    
    # update the highlighting
    self._highlightGroups()


  def highlightSelectedCell(self, x, y):
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
      self._getGameGrid()[self.selectedCell.x][self.selectedCell.y].setStyleSheet(self.selectedCell.originalStyle)
  
    # register the newly selected cell
    self.selectedCell = PyQtGUI.SelectedCell(x, y, self._getGameGrid()[x][y].styleSheet())
  
    # highlight the new cell
    self._getGameGrid()[x][y].setStyleSheet(self.CELL_STYLE_HIGHLIGHTED)
    self._setStatusText("{}x{}".format(x, y))
  
  
  def showBoardGeneratorWindow(self):
    """ Display the board generator window """
    
    mainWindowStatusFn = self.notifyStatus
    
    # create the dialog box and pipe the status notifications to it
    genDialog = PyQtGUI.BoardGeneratorDialog(self.mainWindow, gui=self)
    self.notifyStatus = genDialog.setStatus
    
    # show the dialog
    genDialog.show()
    genDialog.exec_()
    
    # revert status messages back to the main window
    self.notifyStatus = mainWindowStatusFn