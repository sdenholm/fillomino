import os
import logging
import sys
import time

import yaml

logger = logging.getLogger(__name__)

import datetime
from datetime import timedelta

import numpy as np

from fillomino.board import Board
from fillomino.display import PyQtGUI
from fillomino.database import Database

from boardGenerator.generator import BoardGenerator, GenerationFailedError

class Controller(object):
  
  @staticmethod
  def _loadConfigFile(configFileLoc):
    """ Load in the data from the yaml config file """
    
    # CHECK: file location exists
    if not os.path.exists(configFileLoc):
      raise FileNotFoundError("Cannot find config file at: {}".format(configFileLoc))
    
    # load and return the config data
    with open(configFileLoc, 'r') as f:
      configData = yaml.safe_load(f)
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
    self.databaseLoc = self.configData["database-file"]
    self.rows        = self.configData["rows"]
    self.columns     = self.configData["columns"]
    
    # make sure there is a board database
    if not os.path.exists(self.databaseLoc):
      raise SystemError("Board database does not exist")

    # connect to the database
    self.db = Database(self.databaseLoc)
    self.db.connect()
    
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
    
  
  def getBoardGenerationStatus(self):
    return self.boardGenerationStatus
  
  def getBoardGenerationProgress(self):
    return self.boardGenerationProgress
  
  def _updateConfig(self, **kwargs):
    """ Update the configuration data """
    Controller._updateConfigFile(self.configFileLoc, kwargs)
  
  def getBoardsInfo(self):
    """ Get information about each of the board types available """
    return self.db.getBoardsInfo()
  
  def loadBoard(self, rows, columns, boardID=None):
    """
    # For the given dimensions, either load in a random board or the board
    # with the specifc ID (if it exists)
    #
    """
    
    # load in a random board
    if boardID is None:
      boardInfo = self.db.loadRandomBoard(rows=rows, columns=columns)
      if boardInfo is None:
        self.gui.notifyStatus("Failed to load a random {}x{} board".format(rows, columns))
        return
      
    # load in a specific board's info
    else:
      
      # make sure the board exists
      boardInfo = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      if boardInfo is None:
        self.gui.notifyStatus("No {}x{} board with ID {} exists".format(rows, columns, boardID))
        return
    
    # set the new row and column dimensions
    self.rows    = rows
    self.columns = columns
    
    """
    # randList = list(map(int, np.random.randint(0,9,self.rows*self.columns)))
    initList = [8] * 6 + [0] * 14 + [0] * 40 + [7] * 6 + [0] * 14 + [0] * 16 * 20
    finalList = [8] * 8 + [0] * 12 + [0] * 40 + [7] * 7 + [0] * 13 + [0] * 16 * 20

    boardInfo = {
      "initialBoard": initList,
      "finalBoard": finalList,
      "stats": {}
    }
    """
    
    # create a new board from this info
    #self.board = Board.getExampleBoard()
    self.board = Board.createBoard(self.rows, self.columns,
                                   initialValuesList=boardInfo["initialBoard"],
                                   finalValuesList=boardInfo["finalBoard"],
                                   stats=boardInfo["stats"])
    
    
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
  
  def getNumberOfBoards(self, rows, columns):
    """ How many (rows x columns) boards are in the database """
    
    boardInfo = self.getBoardsInfo()
    if boardInfo is None or not boardInfo.get((rows, columns), False):
      return 0
    else:
      return boardInfo.get((rows, columns))["length"]
  
  def loadRandomBoard(self):
    """ Return a random board from the database """
    
    rows    = self.rows
    columns = self.columns
    
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
  
  def generateBoards(self, numberOfBoards, rows, columns, maxAttempts=50):
    """ Generate and store new boards"""
    
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
            self.gui.notifyStatus("Board generation halted")
            return
          
          time.sleep(0.01)
          break
          
        # failed to generate a board
        except GenerationFailedError as err:
          
          # if we have been given the signal to stop
          if self.stopGeneration:
            self.stopGeneration = False
            self.gui.notifyStatus("Board generation halted")
            return
          
          # if we have reached our attempt limit, raise an error
          attempt += 1
          if attempt >= maxAttempts:
            errMsg = "Exceeded maximum ({}) number of attempts to generate a {}x{} board"\
                      .format(maxAttempts, rows, columns)
            raise GenerationFailedError(errMsg)

    self.boardGenerationStatus   = "Finished generation"
    self.boardGenerationProgress = 1.0
  
  def storeGeneratedBoard(self, initialBoard, finalBoard):
    """ Store a newly generated board in the database """
    
    # row and column info from the board
    rows, columns = finalBoard.getBoardDimensions()
    
    # ID is just the current timestamp
    created      = datetime.datetime.utcnow()
    boardID      = int(np.floor(created.timestamp()*1000))
    creationDate = str(created)
    
    # boards as lists
    initialBoardList = list(map(int, initialBoard.getValues().flatten()))
    finalBoardList   = list(map(int, finalBoard.getValues().flatten()))
    
    # store the board
    self.db.storeBoard(rows         = rows,
                       columns      = columns,
                       boardID      = boardID,
                       initialBoard = initialBoardList,
                       finalBoard   = finalBoardList,
                       creationDate = creationDate,
                       stats        = {})
    
  
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
    
    # clear errors
    self.board.clearErrors()

    # update the gui
    self.gui.displayNewBoard(self.board)