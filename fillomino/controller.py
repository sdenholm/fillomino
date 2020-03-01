import os
import logging
logger = logging.getLogger(__name__)

import numpy as np

from fillomino.board import Board
from fillomino.display import GUI
from fillomino.database import Database

class Controller(object):
  
  def __init__(self, databaseLoc):
    

    self.rows    = 20
    self.columns = 20
    
    # make sure there is a board database
    if not os.path.exists(databaseLoc):
      raise SystemError("Board database does not exist")

    # connect to the database
    self.db = Database(databaseLoc)
    self.db.connect()
    
    # create a board
    self.board = Board(rows=self.rows, columns=self.columns)
    
    # create a GUI
    self.gui = GUI(self, self.board)
    
    
  
  def run(self):
    self.gui.run()
  
  def updateBoard(self, x, y, value):
    """ Update the value of a board entry """
    
    self.board.updateCell(x, y, value)
    self.board.updateGroups()
    
    self.gui.updateCell(x,y,value)
    self.gui.highlightValidGroups(self.board.getValidGroups())
    self.gui.highlightInvalidGroups(self.board.getInvalidGroups())
  
  def newBoard(self):
    """ Return a random board from the database """
    
    # load in a board's info
    #boardInfo = self.db.loadRandomBoard(rows=self.rows, columns=self.columns)

    boardInfo = {
      "initialBoard": list(map(int, np.random.randint(0,9,self.rows*self.columns)))
    }

    # create a new board
    self.board = Board.createBoardFromList(self.rows, self.columns, boardInfo["initialBoard"])
    self.board.updateGroups()
    
    # update the gui
    self.gui.setBoard(self.board)
    self.gui.highlightValidGroups(self.board.getValidGroups())
    self.gui.highlightInvalidGroups(self.board.getInvalidGroups())
    
  
  def resetBoard(self):
    """ Reset the board state back to its initial values """
    
    # reset the board
    self.board.resetBoard()
    
    # update the gui
    self.gui.setBoard(self.board)
    
    
  def clearErrors(self):
    """ Clear any cells that don't match the final board values """
    
    print("clear errors")
    pass