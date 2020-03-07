from concurrent import futures
import os
import logging
import sys
import time
from multiprocessing.pool import ThreadPool

import yaml

logger = logging.getLogger(__name__)

import datetime
from datetime import timedelta

import numpy as np

from fillomino.board import Board
from fillomino.display import PyQtGUI
from fillomino.database import Database, DatabaseSetup

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
      DatabaseSetup.createDatabase(self.databaseLoc)
    self.db = Database(self.databaseLoc)
    
    # disable board editing
    self.editingEnabled = False
    
    # signals and status for board generation
    self.stopGeneration = False
    self.boardGenerationStatus   = ""
    self.boardGenerationProgress = 0
    
    # create a blank board
    self.board = Board(rows=self.rows, columns=self.columns)
    
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
  
  def loadBoard(self, rows, columns, boardID=None):
    """
    # For the given dimensions, either load in a random board or the board
    # with the specifc ID (if it exists)
    #
    """
    
    # load in a random board
    if boardID is None:
      board = self.db.loadRandomBoard(rows=rows, columns=columns)
      #board = Board.getExampleBoard()
      #board = BoardGenerator.defineInitialBoardState(board)
      if board is None:
        self.gui.notifyStatus("Failed to load a random {}x{} board".format(rows, columns))
        return
      
    # load in a specific board's info
    else:
      
      # make sure the board exists
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      if board is None:
        self.gui.notifyStatus("No {}x{} board with ID {} exists".format(rows, columns, boardID))
        return
    
    # set the new row and column dimensions
    self.board   = board
    self.rows    = rows
    self.columns = columns

    # create a new board from this info
    #self.board = Board.getExampleBoard()
    
    # update the gui
    self.gui.displayNewBoard(self.board)

    # enable editing
    self.editingEnabled = True
  
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

    # display finished message
    self.gui.boardComplete()
  

  
  def loadRandomBoard(self):
    """ Return a random board from the database """


    rows    = self.rows
    columns = self.columns

    self.loadBoard(rows, columns)
    return
    
    if self.getNumberOfBoards(rows, columns) == 0:
      self.gui.notifyStatus("No {}x{} boards in the database".format(rows, columns))
    else:
      self.loadBoard(rows, columns)
  
  def canEditBoard(self):
    """ Can the user edit the board """
    return self.editingEnabled

  
  def stopBoardGeneration(self):
    """ Signal any current board generation to stop """
    self.stopGeneration = True

  
  @staticmethod
  def _parallelGenerate(dimensions, maxAttempts=50):
    """ Function called by processes in generateBoards() """
    
    # get the dimensions
    rows, columns = dimensions
    
    # try <maxAttempt> times to generate a board
    for _ in range(maxAttempts):
      try:
      
        # generate the board
        generator = BoardGenerator(rows=rows, columns=columns)
        newBoard, timeTaken = generator.generate()
        return newBoard
    
      # failed to generate a board
      except GenerationFailedError:
        pass
      
      time.sleep(0.1)
      
    # we have reached our attempt limit, raise an error
    errMsg = "Exceeded maximum ({}) number of attempts to generate a {}x{} board" \
      .format(maxAttempts, rows, columns)
    raise GenerationFailedError(errMsg)
  
  
  def generateBoards(self, numberOfBoards, rows, columns):
    """ Generate and store new boards"""
  
    # CHECK: rows and columns are valid
    if rows < self.board.MIN_BOARD_ROWS or columns < self.board.MIN_BOARD_COLUMNS:
      self.boardGenerationStatus = "ERROR: minimum dimensions: ({}x{})" \
        .format(self.board.MIN_BOARD_ROWS, self.board.MIN_BOARD_COLUMNS)
      self.boardGenerationProgress = 0
      return
  
    # reset stop signal and status
    self.stopGeneration = False
    self.boardGenerationStatus = "Generating..."
    self.boardGenerationProgress = 0
    
    # create a process pool to cycle through each board generation
    with futures.ProcessPoolExecutor() as executor:
      for board in executor.map(Controller._parallelGenerate,
                                [(rows, columns)]*numberOfBoards):
        
        # store the board
        self.storeGeneratedBoard(board)
  
        # update the status
        self.boardGenerationProgress += 1/numberOfBoards
  
        # if we have been given the signal to stop
        if self.stopGeneration:
          self.stopGeneration = False
          self.boardGenerationStatus = "Board generation halted"
          return
  
    
    self.boardGenerationStatus = "Generation Complete"
    self.boardGenerationProgress = 1.0

  def DEPgenerateBoards(self, numberOfBoards, rows, columns, maxAttempts=50, numProcessors=4):
    """ Generate and store new boards"""
    
    # CHECK: rows and columns are valid
    if rows < self.board.MIN_BOARD_ROWS or columns < self.board.MIN_BOARD_COLUMNS:
      self.boardGenerationStatus = "ERROR: minimum dimensions: ({}x{})"\
                        .format(self.board.MIN_BOARD_ROWS, self.board.MIN_BOARD_COLUMNS)
      self.boardGenerationProgress = 0
      return
    
    
    # board generator
    generator = BoardGenerator(rows=rows, columns=columns)
    
    # reset stop signal and status
    self.stopGeneration = False
    self.boardGenerationStatus   = "Generating..."
    self.boardGenerationProgress = 0
    
    # generate <numberOfBoards> boards
    for i in range(numberOfBoards):
      
      # try <maxAttempt> times to generate a board
      attempt = 0
      time.sleep(0.01)
      while True:
        try:
          
          # generate the board
          initialBoard, finalBoard, timeTaken = generator.generate()
          
          # store the board
          self.storeGeneratedBoard(initialBoard, finalBoard)
          
          # update the status
          self.boardGenerationProgress = (i+1) / numberOfBoards
          
          # if we have been given the signal to stop
          if self.stopGeneration:
            self.stopGeneration = False
            self.boardGenerationStatus = "Board generation halted"
            return
          
          time.sleep(0.01)
          break
          
        # failed to generate a board
        except GenerationFailedError as err:
          
          # if we have been given the signal to stop
          if self.stopGeneration:
            self.stopGeneration = False
            self.boardGenerationStatus = "Board generation halted"
            return
          
          # if we have reached our attempt limit, raise an error
          attempt += 1
          if attempt >= maxAttempts:
            errMsg = "Exceeded maximum ({}) number of attempts to generate a {}x{} board"\
                      .format(maxAttempts, rows, columns)
            raise GenerationFailedError(errMsg)

    self.boardGenerationStatus   = "Generation Complete"
    self.boardGenerationProgress = 1.0
  
  def storeGeneratedBoard(self, board):
    """ Store a newly generated board in the database """
    
    # row and column info from the board
    rows, columns = board.getBoardDimensions()
    
    # ID is just the current timestamp
    created      = datetime.datetime.utcnow()
    boardID      = int(np.floor(created.timestamp()*1000))
    creationDate = str(created)
    
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
    """ Clear the board and reset all baord-specific information"""
    
    self.board = None
    
    # tell the gui to clear the board
    self.gui.clearBoard()
  
  def resetBoard(self):
    """ Reset the board state back to its initial values """
    
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