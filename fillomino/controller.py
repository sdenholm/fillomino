import os

import numpy as np

from fillomino.board import Board
from fillomino.database import Database

class Controller(object):
  
  def __init__(self, databaseLoc, rows=20, columns=20):
    
    self.rows    = rows
    self.columns = columns
    
    # make sure there is a board database
    if not os.path.exists(databaseLoc):
      raise SystemError("Board database does not exist")

    # connect to the database
    self.db = Database(databaseLoc)
    self.db.connect()
  
  def getNewBoard(self):
    """ Return a random board from the database """
    
    # load in a board's info
    #boardInfo = self.db.loadRandomBoard(rows=self.rows, columns=self.columns)

    boardInfo = {
      "initialBoard": list(map(int, np.random.randint(1,9,self.rows*self.columns)))
    }
    
    # create the board
    return Board.createBoardFromList(self.rows, self.columns, boardInfo["initialBoard"])