import logging
logger = logging.getLogger(__name__)

import numpy as np

class Board(object):
  
  @staticmethod
  def createBoard(rows, columns, initialValuesList, finalValuesList, stats):
    """ Create a board using lists """
    
    initialArr = np.zeros((rows, columns), np.int8)
    finalArr   = np.zeros((rows, columns), np.int8)

    # convert the lists to arrays
    for row in range(rows):
      for column in range(columns):
        initialArr[row][column] = initialValuesList[row*rows + column]
        finalArr[row][column]   = finalValuesList[row*rows + column]
    
    
    # create the board
    board = Board(rows=rows, columns=columns,
                  initialValues=initialArr,
                  finalValues=finalArr,
                  stats=stats)
    
    """
    # set its values
    for row in range(rows):
      for column in range(columns):
        board.values[row][column] = boardList[row*rows + column]
    
    # set this as the initial state
    board.initialValues = board.values.copy()
    """
    
    return board
  
  
  def __init__(self, rows, columns, initialValues=None, finalValues=None, stats=None):
    """
    # -initialValues: (array)
    # -finalValues:   (array)
    # -stats:         (dictionary)
    #
    """
    
    # if no initial values given then set to 0s (all blank)
    if initialValues is None:
      initialValues = np.zeros((rows, columns), np.int8)
      
    # no stats
    if stats is None:
      stats = {}
      
    self.rows    = rows
    self.columns = columns
    self.values  = initialValues.copy()
    
    self.initialValues = initialValues
    self.finalValues   = finalValues
    self.stats         = stats
    
    # groups:
    #  -groups with the correct number of members
    #  -groups with more than the max number of members
    #  -all other groups
    self.invalidGroups = {}
    self.validGroups   = {}
    self.orphanGroups  = {}
    
    # gather the group information
    self.updateGroups()
  
  
  def getValues(self):        return self.values
  def getCellValue(self,row,col): return self.values.item(row,col)
  def getValidGroups(self):   return self.validGroups
  def getInvalidGroups(self): return self.invalidGroups
  def getOrphanGroups(self):  return self.orphanGroups
  
  
  
  def resetBoard(self):
    """ Resets the board to its initial values """
    
    # set the values
    self.values = self.initialValues.copy()
    
    # update the groups
    self.updateGroups()
    
    
  def updateCell(self, x, y, value):
    """ Update the value of an individual cell """
    
    # can't update initial value cells
    if self.initialValues[x][y] != 0:
      return
    
    # update cell and the group info
    self._setCellValue(x, y, value)
    self.updateGroups()
  
  
  
  def clearErrors(self):
    """
    # Find the differences between the current and final values and set any differences to 0
    """
    
    # no final values to compare to
    if self.finalValues is None:
      return
    
    # set every difference to 0
    #  -ignore blank cells
    #  -ignore cells defined by the initial values
    for row in range(self.rows):
      for col in range(self.columns):
        if self.values[row][col] != 0 and self.initialValues[row][col] == 0 and\
           self.values[row][col] != self.finalValues[row][col]:
          self._setCellValue(row, col, 0)
    
    # update the group information
    self.updateGroups()
    
    
  def _setCellValue(self, x, y, value):
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
            self.orphanGroups[0].append([(row, col)])
            processedLocations.append((row, col))
          
          else:
            
            # get this group of numbers, ignoring the current cell
            newGroup = self._findNeighbourMatches(row, col, cellVal, [(row, col)])
            
            # is it a valid, invalid, or orphan group
            if len(newGroup) == cellVal:
              self.validGroups[cellVal].append(newGroup)
            elif len(newGroup) > cellVal:
              self.invalidGroups[cellVal].append(newGroup)
            else:
              self.orphanGroups[cellVal].append(newGroup)
            
            # processed these cells
            processedLocations += newGroup
    
    #print("validGroups========")
    #for k,v in self.validGroups.items():
    #  print(k, v)
    #print("invalidGroups========")
    #for k,v in self.invalidGroups.items():
    #  print(k, v)
    #print("orphanGroups========")
    #for k,v in self.orphanGroups.items():
    #  print(k, v)
    
  def _findNeighbourMatches(self, row, column, number, locations=None):
    """
    # From the given cell, find the cells with matching numbers in the
    # N,S,W,E directions, ignoring the loctions we have already found.
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
  