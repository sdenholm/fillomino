import os
import logging
logger = logging.getLogger(__name__)

import datetime
from datetime import timedelta

import numpy as np

from fillomino.board import Board
from fillomino.display import GUI
from fillomino.database import Database

from boardGenerator.generator import BoardGenerator

class Controller(object):
  
  def __init__(self, databaseLoc):
    
    # default rows
    self.rows    = 20
    self.columns = 20
    
    # make sure there is a board database
    if not os.path.exists(databaseLoc):
      raise SystemError("Board database does not exist")

    # connect to the database
    self.db = Database(databaseLoc)
    self.db.connect()
    
    # disable board editing
    self.editingEnabled = False
    
    # create a blank board
    #self.board = Board(rows=self.rows, columns=self.columns)
    generator = BoardGenerator(rows=self.rows, columns=self.columns)
    self.board = generator.generate()
    
    
    # create a GUI
    self.gui = GUI(self, self.board)
    
    
    
  def loadBoard(self, rows, columns, boardID=None):
    """
    # For the given dimensions, either load in a random board or the board
    # with the specifc ID (if it exists)
    #
    """
    
    # load in a random board
    if boardID is None:
      #boardInfo = self.db.loadRandomBoard(rows=rows, columns=columns)
      boardInfo = 777
      if boardInfo is None:
        raise SystemError("Failed to load a random {}x{} board".format(rows, columns))
      
    # load in a specific board's info
    else:
      
      # make sure the board exists
      boardInfo = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      if boardInfo is None:
        raise SystemError("No {}x{} board with ID {} exists".format(rows, columns, boardID))
    
    # set the new row and column dimensions
    self.rows    = rows
    self.columns = columns
    
    # randList = list(map(int, np.random.randint(0,9,self.rows*self.columns)))
    initList = [8] * 6 + [0] * 14 + [0] * 40 + [7] * 6 + [0] * 14 + [0] * 16 * 20
    finalList = [8] * 8 + [0] * 12 + [0] * 40 + [7] * 7 + [0] * 13 + [0] * 16 * 20

    boardInfo = {
      "initialBoard": initList,
      "finalBoard": finalList,
      "stats": {}
    }

    # create a new board from this info
    self.board = Board.getExampleBoard()
    """
    self.board = Board.createBoard(self.rows, self.columns,
                                   initialValuesList=boardInfo["initialBoard"],
                                   finalValuesList=boardInfo["finalBoard"],
                                   stats=boardInfo["stats"])
    """
    
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
      
    
  def boardComplete(self):
    """ Called when the board is completed """

    # disable editing
    self.editingEnabled = False

    # display finished message
    self.gui.boardComplete()
  
  def newBoard(self):
    """ Return a random board from the database """
    
    rows = 20
    columns = 20
    
    self.loadBoard(rows, columns)
  
  def canEditBoard(self):
    """ Can the user edit the board """
    return self.editingEnabled
  
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