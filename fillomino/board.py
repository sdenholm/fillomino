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
  
  
  def __init__(self, rows, columns, initialValues=None, finalValues=None, stats=None):
    """
    #
    #
    #
    # -initialValues: (array)
    # -finalValues:   (array)
    # -stats:         (dictionary)
    #
    """
    self.rows    = rows
    self.columns = columns
    self.values  = np.zeros((rows, columns), np.int8)
    self.initialValues = self.values.copy()
    
    # groups:
    #  -groups with the correct number of members
    self.validGroups   = {}
    #  -groups with more than the max number of members
    self.invalidGroups = {}
    #  -all other groups
    self.orphanGroups  = {}
    
  def getValues(self):        return self.values
  def getValidGroups(self):   return self.validGroups
  def getInvalidGroups(self): return self.invalidGroups
  
  def resetBoard(self):
    """ Resets the board to its initial values """
    self.values = self.initialValues.copy()
    
  def updateCell(self, x, y, value):
    """ Update the value of an individual cell """
    self.values[x][y] = int(value)
  

  
  def updateGroups(self):
    """
    # Group all of the board cells into groups
    #
    """
    
    
    # reset the group info
    for i in range(10):
      self.validGroups[i]   = []
      self.invalidGroups[i] = []
      self.orphanGroups[i]  = []
    
    processedLocations = []
    
    # look a t each cell
    for row in range(self.rows):
      for col in range(self.columns):
        
        # if we haven't processed it yet
        if (row,col) not in processedLocations:
          
          # get cell value
          cellVal = self.values[row][col]
          
          # empty cells are always orphans
          if cellVal == 0:
            self.orphanGroups[0].append((row, col))
            processedLocations.append((row, col))
          
          else:
            
            # get this group of numbers
            newGroup = self._findNeighbourMatches(row, col, cellVal)
            
            # is it a valid, invalid, or orphan group
            if len(newGroup) == cellVal:
              self.validGroups[cellVal].append(newGroup)
            elif len(newGroup) > cellVal:
              self.invalidGroups[cellVal].append(newGroup)
            else:
              self.orphanGroups[cellVal].append(newGroup)
            
            # processed these cells
            processedLocations += newGroup
  
    
  def _findNeighbourMatches(self, row, column, number, locations=None):
    """
    # From the given cell, find the cells with matching numbers in the
    # N,S,W,E directions, ifnoring the loctions we have already found.
    # Called recursively to find all the members of this number group
    #
    # row:
    # column:
    # number:    cell value to match
    # locations: list of locations to ignore
    #
    """
    
    if locations is None:
      locations = []
    
    # north
    newColumn = column-1
    if newColumn >= 0 and (row, newColumn) not in locations:
      if self.values[row][newColumn] == number:
        locations.append((row, newColumn))
        self._findNeighbourMatches(row, newColumn, number, locations)
    
    # south
    newColumn = column+1
    if newColumn < self.columns and (row, newColumn) not in locations:
      if self.values[row][newColumn] == number:
        locations.append((row, newColumn))
        self._findNeighbourMatches(row, newColumn, number, locations)
        
    # west
    newRow = row-1
    if newRow >= 0 and (newRow, column) not in locations:
      if self.values[newRow][column] == number:
        locations.append((newRow, column))
        self._findNeighbourMatches(newRow, column, number, locations)
        
    # east
    newRow = row+1
    if newRow < self.rows and (newRow, column) not in locations:
      if self.values[newRow][column] == number:
        locations.append((newRow, column))
        self._findNeighbourMatches(newRow, column, number, locations)
    
    return locations
  