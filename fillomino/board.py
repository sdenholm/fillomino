

import numpy as np

from fillomino.database import Database

class Board(object):
  
  @staticmethod
  def createBoardFromList(rows, columns, boardList):
    """ Create a board with its layout given by a 1D list """
    
    # create a blank board
    board = Board(rows=rows, columns=columns)
    
    # set its values
    for row in range(rows):
      for column in range(columns):
        board.values[row][column] =  boardList[row*rows + column]
        
    return board
  
  
  def __init__(self, rows, columns):
    
    #self.boardDB = Database("boards.db")
    
    self.rows    = rows
    self.columns = columns
    self.values  = np.zeros((rows, columns), np.int8)
  
  def getValues(self):
    return self.values