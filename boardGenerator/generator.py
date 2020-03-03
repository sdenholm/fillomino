
from scipy import signal

import numpy as np

from fillomino.board import Board

class BoardGenerator(object):
  
  @staticmethod
  def hasIslandOnes(board):
    """
    # Find areas of the board where a single blank space is surrounded by 1s
    #
    # Three possible locations:
    #  -2-point match on a board corner
    #  -3-point match on a board edge
    #  -4-point match in the middle of the board
    #
    """
    
    # get the board dimensions
    rows, columns = board.getBoardDimensions()
    
    # convolution filter looking for islands
    islandFilter = np.array([[0,1,0],
                             [1,0,1],
                             [0,1,0]])
    
    # find islands
    matches = signal.convolve2d(board.getValues(), islandFilter, mode="same")
    
    # are there any 2-point matches in a corner
    if matches[0,0] == 2 or matches[rows-1,0] == 2 or\
       matches[0,columns-1] == 2 or matches[rows-1,columns-1] == 2:
      return True
    
    # are there any 3-point matches on an edge
    if (matches[0,:] == 3).any() or (matches[rows-1,:] == 3).any() or\
       (matches[:,0] == 3).any() or (matches[:,columns-1] == 3).any():
      return True
    
    # are there any 4-point matches in the centre
    if np.argwhere(matches[1:-1,1:-1] == 4).size > 0:
      return True
    
    return False

  def __init__(self, rows, columns):
    
    self.rows = rows
    self.columns = columns
  
  @staticmethod
  def addInitialOnes(board, numOnes):
    """ Add in 1's at random places of the board, making sure they're all valid """
    
    # locations of cells we've added
    pastCells = []
    
    # get board dimensions
    rows, columns = board.getBoardDimensions()
    
    for i in range(numOnes):
      
      # loop until we add a valid "1"
      while True:
        row = np.random.randint(0, rows)
        col = np.random.randint(0, columns)
        
        # make sure we haven't randomly selected this location before
        if (row, col) in pastCells:
          continue
        
        # set the location to 1
        board.values.itemset(row, col, 1)
      
        # make sure we don't have any island 1's
        if not BoardGenerator.hasIslandOnes(board):
        
          # if the board is still valid after our change, move on
          board.updateGroups()
          if board.isBoardValid():
            pastCells.append((row,col))
            break
      
        # we made the board invalid, so undo our change
        board.values.itemset(row, col, 0)
    
    return board
  
  def generate(self):
    
    # create a new blank board
    bd = Board(rows=self.rows, columns=self.columns)
    
    # add in some random 1's
    numOnes = np.random.randint(40, 50)
    
    bd = BoardGenerator.addInitialOnes(bd, numOnes)
    
    # number of free spaces
    freeSpaces = np.product(bd.getBoardDimensions()) - numOnes
    
    #
    
    return bd

    