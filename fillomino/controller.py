
import logging
import threading

logger = logging.getLogger(__name__)

import os
import time
import yaml
import datetime

import numpy as np

from concurrent import futures

from fillomino.board import Board
from fillomino.display import PyQtGUI
from fillomino.database import Database, DatabaseInfo

from boardGenerator.generator import BoardGenerator, GenerationFailedError

class Controller(object):
  
  
  @staticmethod
  def _loadConfigFile(configFileLoc):
    """ Load in the data from the yaml config file """
    
    # CHECK: file location exists
    if not os.path.exists(configFileLoc):
      raise FileNotFoundError("Cannot find config file at: {}".format(configFileLoc))
    
    # load the config data
    with open(configFileLoc, 'r') as f:
      configData = yaml.safe_load(f)
      
    # check we have the correct data
    entryNames = ["database-file", "rows", "columns", "version"]
    for entry in entryNames:
      if configData.get(entry, None) is None:
        raise SystemError("Config file is missing an entry for {}".format(entry))
      
    return configData
  
  @staticmethod
  def _updateConfigFile(configFileLoc, newConfigData):
    """ Update an entry in the config file """

    # CHECK: file location exists
    if not os.path.exists(configFileLoc):
      raise FileNotFoundError("Cannot find config file at: {}".format(configFileLoc))

    # load the existing config data
    with open(configFileLoc, 'r') as f:
      configData = yaml.safe_load(f)
    
    # change the data
    configData.update(newConfigData)
    
    # write the data
    with open(configFileLoc, 'w') as f:
      yaml.safe_dump(configData, f)
  
  @staticmethod
  def aboutText(textType=None):
    """ Text giving the game info """
    
    if textType == "richtext":
      return """Fillomino<p>By Stewart Denholm<p><a href=https://github.com/sdenholm>GitHub</a>"""
    
    else:
      return """Fillomino\nBy Stewart Denholm\nGitHub: github.com/sdenholm"""
  
  @staticmethod
  def howToPlayText(textType=None):
    """ Text describing how to play the game """
    
    msg = """
<h3>How to Play</h3><p>
1) Fill in the blanks using the digits 1-9 to create regions, called polyominoes.<p>
2) A region must contain as many cells as its number value e.g., three number 3s together will
make a region, or four number 4s together, five number 5s, etc.<p>
3) Regions with the same number cannot touch. For example, two regions of four 4s cannot
be neighbours.<p>
4) When the board is filled, you win!<p><p>
<h3>Generating Boards</h3><p>
To play, you must first generate boards:<p>
1) From the menu, select [Boards]=>[Generate New Boards]<p>
2) Choose the board dimensions, and how many boards to generate.<p>
3) Click Generate.<p>
When generation is done, select [File]=>[Load Random Board] from the main menu to play one of the boards.
"""
    
    if textType == "richtext":
      return  msg
    else:
      return msg.replace("<p>", "\n\n").replace("<h3>", "").replace("<\h3>", "")
  
  def __init__(self, configFileLoc):
    
    self.configFileLoc = configFileLoc
    
    # load the config data from the config file
    self.configData = Controller._loadConfigFile(configFileLoc)

    # config data:
    #  -database location
    #  -default rows x columns
    #  -version
    self.databaseLoc = self.configData["database-file"]
    self.rows        = self.configData["rows"]
    self.columns     = self.configData["columns"]
    self.version     = self.configData["version"]
    
    # make sure there is a board database
    #if not os.path.exists(self.databaseLoc):
    #  raise SystemError("Board database does not exist")

    # board database
    #  -if the database doesn't exist, create it
    if not os.path.exists(self.databaseLoc):
      DatabaseInfo.createDatabase(self.databaseLoc)
    self.db = Database(self.databaseLoc)
    
    # disable board editing
    self.editingEnabled = False
    
    # signals and status for board generation
    self.stopGeneration = False
    self.boardGenerationStatus   = ""
    self.boardGenerationProgress = 0
    
    # stats stuff
    self.startTime = None

    self.board = None
    self.gui = None
    
    # clear the board
    self.clearBoard()

    # create a GUI
    self.gui = PyQtGUI(self, self.board)
    

  def _updateConfig(self, **kwargs):
    """ Update the configuration data """
    Controller._updateConfigFile(self.configFileLoc, kwargs)
  
  def getBoardGenerationStatus(self):
    return self.boardGenerationStatus
  
  def getBoardGenerationProgress(self):
    return self.boardGenerationProgress
  
  def getBoardsInfo(self):
    """ Get information about each of the board types available """
    return self.db.getBoardsInfo()

  def getNumberOfBoards(self, rows, columns):
    """ How many (rows x columns) boards are in the database """
  
    boardInfo = self.getBoardsInfo()
    if boardInfo is None or not boardInfo.get((rows, columns), False):
      return 0
    else:
      return boardInfo.get((rows, columns))["length"]
  

    
    
  def _processLoadedBoard(self, board):
    """ Remember and display a newly loaded board """
    
    # set the new row and column dimensions
    self.board = board
    self.rows, self.columns = board.getBoardDimensions()
    
    # update the gui
    self.gui.displayNewBoard(self.board)

    # enable editing
    self.editingEnabled = True
    
    # start the boardTimer
    self.startTime = datetime.datetime.utcnow()
  
  
  def run(self):
    self.gui.run()
  
  def updateBoard(self, x, y, value):
    """ Update the value of a board entry """
    
    if not self.editingEnabled:
      return
    
    # update the cell value in the board and gui
    self.board.updateCell(x, y, value)
    self.gui.updateCell(x,y)
    
    # if the board is complete
    if self.board.isBoardComplete():
      self.boardComplete()
      
      
  def setBoardDimensions(self, rows, columns):
    """ Change the board dimensions """
    
    # if the board is already set to these dimensions
    if rows == self.rows and columns == self.columns:
      return
    
    # update the rows and columns info here and in the config file
    self.rows    = rows
    self.columns = columns
    self._updateConfig(rows=rows, columns=columns)
    
    # disable board editing
    self.editingEnabled = False

    # create a blank board
    self.board = Board(rows=self.rows, columns=self.columns)

    # update the gui
    self.gui.displayNewBoard(self.board)
    
    
  def boardComplete(self):
    """ Called when the board is completed """

    # disable editing
    self.editingEnabled = False
    
    # calulate the solve time
    if self.startTime is None:
      raise SystemError("Board was never started")
    solveTime = (datetime.datetime.utcnow() - self.startTime).total_seconds()

    # update and store the board stats
    self.board.updateSolveStats(solveTime)
    self.db.updateBoardStats(self.board)
    
    # display finished message
    self.gui.boardComplete()
  
  
  def deleteBoard(self):
    """ Delete the current board from the database """
    
    # if the user confirms this is okay
    if self.board.getID() is not None and\
       self.gui.confirmAction("Are you sure you want to delete this board?"):
      
      # remove the board from the database and clear it
      self.db.removeBoard(*self.board.getBoardDimensions(), self.board.getID())
      self.clearBoard()
      
      # tell the GUI we've updated our board numbers
      self.gui.addedNewBoards()

  def loadBoard(self, boardID):
    """
    # For the given dimensions, load in a board with the specifc ID
    #
    """
    
    rows    = self.rows
    columns = self.columns
    
    # check we have boards
    if self.getNumberOfBoards(rows, columns) == 0:
      self.gui.notifyStatus("No {}x{} boards in the database".format(rows, columns))
      return
  
    # load in a specific board's info
    board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
    if board is None:
      self.gui.notifyStatus("No {}x{} board with ID {} exists".format(rows, columns, boardID))
      return
  
    self._processLoadedBoard(board)
    
  
  def loadUnsolvedBoard(self):
    """ Return a random, unsolved board from the database """
    
    rows    = self.rows
    columns = self.columns

    # check we have boards
    if self.getNumberOfBoards(rows, columns) == 0:
      self.gui.notifyStatus("No {}x{} boards in the database".format(rows, columns))
      return

    # get the ID of the current board and exclude it from the load
    if self.board:
      currentBoardID = self.board.getID()
    else:
      currentBoardID = None

    # load in an unsolved board
    board = self.db.loadUnsolvedBoard(rows=rows, columns=columns, excludeID=currentBoardID)
    if board is None:
      self.gui.notifyStatus("Failed to load an unsolved {}x{} board".format(rows, columns))
      return

    # use and display this board
    self._processLoadedBoard(board)
  
  
  def loadRandomBoard(self):
    """ Return a random board from the database """
    
    rows    = self.rows
    columns = self.columns
    
    # check we have boards
    if self.getNumberOfBoards(rows, columns) == 0:
      self.gui.notifyStatus("No {}x{} boards in the database".format(rows, columns))
      return
    
    # get the ID of the current board and exclude it from the load
    if self.board:
      currentBoardID = self.board.getID()
    else:
      currentBoardID = None
    
    # load in a random board
    board = self.db.loadRandomBoard(rows=rows, columns=columns, excludeID=currentBoardID)
    # board = Board.getExampleFinishedBoard()
    # board = Board.getExampleBoard()
    # board = BoardGenerator.defineInitialBoardState(board)
    if board is None:
      self.gui.notifyStatus("Failed to load a random {}x{} board".format(rows, columns))
      return
    
    # use and display this board
    self._processLoadedBoard(board)
  
  
  def canEditBoard(self):
    """ Can the user edit the board """
    return self.editingEnabled

  
  def stopBoardGeneration(self):
    """ Signal any current board generation to stop """
    self.stopGeneration = True

  
  @staticmethod
  def _parallelGenerate(dimensions, maxAttempts=50):
    """
    # Function called by processes in generateBoards(). Creates a new
    # generator and attempts <maxAttempts> times to generate a board with
    # the given dimensions
    #
    """
    
    # get the dimensions
    rows, columns = dimensions
    
    # try <maxAttempt> times to generate a board
    for _ in range(maxAttempts):
      try:
        
        # if we've been told to stop
        #print(Controller.GENERATION_ENABLED)
        #if self.stopGeneration:
        #  return None
        #  #raise GenerationFailedError("Generation is disabled")
        
        # generate and return the board
        generator = BoardGenerator(rows=rows, columns=columns)
        return generator.generate()
    
      # failed to generate a board
      except GenerationFailedError:
        pass
      
      time.sleep(0.1)
      
    # we have reached our attempt limit, raise an error
    errMsg = "Exceeded maximum ({}) number of attempts to generate a {}x{} board" \
      .format(maxAttempts, rows, columns)
    raise GenerationFailedError(errMsg)
  
  
  def generateBoards(self, numberOfBoards, rows, columns):
    """
    # Generate and store some new boards
    #
    # -numberOfBoards: (int) number of boards to generate
    # -rows:           (int) board rows
    # -columns:        (int) board columns
    #
    """
  
    # CHECK: rows and columns are valid
    if rows < self.board.MIN_BOARD_ROWS or columns < self.board.MIN_BOARD_COLUMNS:
      self.boardGenerationStatus = "ERROR: minimum dimensions: ({}x{})" \
        .format(self.board.MIN_BOARD_ROWS, self.board.MIN_BOARD_COLUMNS)
      self.boardGenerationProgress = 0
      return
  
    # reset stop signal and status
    self.stopGeneration          = False
    self.boardGenerationProgress = 0
    self.boardGenerationStatus   = "Generating {} boards...".format(numberOfBoards)
    
    # create a process pool to cycle through each board generation
    with futures.ProcessPoolExecutor() as executor:
      for board in executor.map(Controller._parallelGenerate,
                                [(rows, columns)]*numberOfBoards):
        
        # if there was an issue with generation
        if board is None:
          continue
        
        # store the board
        self.storeGeneratedBoard(board)
  
        # update the status
        self.boardGenerationProgress += 1/numberOfBoards
  
        # if we have been given the signal to stop
        if self.stopGeneration:
          self.stopGeneration = False
          self.boardGenerationStatus = "Halting: waiting on processes..."
          executor.shutdown()
          self.boardGenerationStatus = "Board generation halted"
          return
    
    # done
    self.boardGenerationStatus = "Generation Complete"
    self.boardGenerationProgress = 1.0

  
  
  def storeGeneratedBoard(self, board):
    """ Store a newly generated board in the database """
    
    # row and column info from the board
    rows, columns = board.getBoardDimensions()
    
    # ID is just the current timestamp
    created      = datetime.datetime.utcnow()
    boardID      = int(np.floor(created.timestamp()*1000000))
    creationDate = str(created.replace(microsecond=0))
    
    # boards as lists
    initialBoardList = list(map(int, board.getInitialValues().flatten()))
    finalBoardList   = list(map(int, board.getFinalValues().flatten()))
    
    # store the board
    self.db.storeBoard(rows         = rows,
                       columns      = columns,
                       boardID      = boardID,
                       initialBoard = initialBoardList,
                       finalBoard   = finalBoardList,
                       creationDate = creationDate,
                       stats        = {})
  
  
  def clearBoard(self):
    """ Clear the board and reset all board-specific information"""
    
    self.board = Board(rows=self.rows, columns=self.columns)
    
    # tell the gui to clear the board
    if self.gui:
      self.gui.clearBoard()
    
  
  def resetBoard(self):
    """ Reset the board state back to its initial values """
    
    #self.boardComplete()
    #return
    
    # reset the board
    self.board.resetBoard()
    
    # update the gui
    self.gui.displayNewBoard(self.board)
    
    # make sure editing is enabled
    self.editingEnabled = True
    
    
  def clearErrors(self):
    """ Clear any cells that don't match the final board values """
    
    if self.editingEnabled:
      
      # clear errors
      self.board.clearErrors()
  
      # update the gui
      self.gui.displayNewBoard(self.board)