import logging
logger = logging.getLogger(__name__)

import numpy as np

class Board(object):
  
  @staticmethod
  def createBoardFromList(rows, columns, boardList):
    """ Create a board with its layout given by a 1D list """
    
    # create a blank board
    board = Board(rows=rows, columns=columns)
    
    # set its values
    for row in range(rows):
      for column in range(columns):
        board.values[row][column] = boardList[row*rows + column]
    
    # set this as the initial state
    board.initialValues = board.values.copy()
    
    return board
  
  
  def __init__(self, rows, columns):
    
    self.rows    = rows
    self.columns = columns
    self.values  = np.zeros((rows, columns), np.int8)
    self.initialValues = self.values.copy()
  
  def getValues(self):
    return self.values
  
  def resetBoard(self):
    """ Resets the board to its initial values """
    self.values = self.initialValues.copy()
    
  def update(self, x, y, value):
    self.values[x][y] = int(value)
    
    print(self._findAllHorizontalMatches(x, y, self.values[x][y]))
    
  def getValidGroups(self):
    validGroups = {
      2:[]
    }
    return validGroups
  
  def getInvalidGroups(self):
    invalidGroups = {
      2: []
    }
    return invalidGroups
  
  
  def _findValidGroups(self):
    pass
  
  def _findAllConnectedNumbers(self, row, column, number):
    
    locations = [(row,column)]
    
    horizontalMatches = self._findAllHorizontalMatches(row, column, number)
    
    pass
  
  def _findAllHorizontalMatches(self, row, column, number):
    """ Look along the row any find the locations of all the numbers that match the given number """
    
    locations = []

    # get all matching numbers to the left
    columnVal = column-1
    while columnVal >= 0:
      print(columnVal)
      print(self.values[row][columnVal])
      if self.values[row][columnVal] == number:
        locations.append((row, columnVal))
        columnVal -= 1
      else:
        break
    
    # get all matching numbers to the right
    columnVal = column+1
    while columnVal < self.columns:
      print(columnVal)
      print(self.values[row][columnVal])
      if self.values[row][columnVal] == number:
        locations.append((row, columnVal))
        columnVal += 1
      else:
        break
    
    return locations
    
  def _findAllVerticalMatches(self, row, column, number):
    pass
  