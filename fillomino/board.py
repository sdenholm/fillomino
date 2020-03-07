
import logging
logger = logging.getLogger(__name__)

import numpy as np


class Board(object):
  
  MIN_BOARD_ROWS    = 5
  MIN_BOARD_COLUMNS = 5
  
  @staticmethod
  def getExampleBoard():
    """ An example 20x20 board for testing """
    
    rows    = 20
    columns = 20
    
    arr = np.zeros((rows, columns), np.int8)
    arr[0]  = [5,0,0,0,4,1,0,0,0,1,0,0,1,3,0,1,2,1,0,1]
    arr[1]  = [0,0,4,1,0,6,3,4,1,0,0,0,6,0,1,0,0,4,0,0]
    arr[2]  = [0,1,0,5,0,0,0,3,0,0,1,0,0,0,2,0,3,0,0,3]
    arr[3]  = [0,0,5,0,5,0,0,0,0,0,0,8,4,1,0,1,9,0,1,0]
    arr[4]  = [0,0,0,0,1,4,1,2,1,0,1,0,0,0,1,0,0,0,0,3]
    arr[5]  = [7,1,9,0,4,0,0,0,0,0,6,0,0,0,7,4,0,1,0,1]
    arr[6]  = [5,0,0,0,0,0,1,0,0,0,1,5,5,1,8,0,0,4,0,0]
    arr[7]  = [0,5,5,1,0,0,0,0,5,0,4,5,0,5,0,0,0,1,3,1]
    arr[8]  = [0,1,0,0,1,5,0,0,1,0,0,0,0,0,0,0,0,0,0,4]
    arr[9]  = [0,3,0,4,3,3,4,0,0,1,6,0,0,1,5,5,1,0,1,0]
    arr[10] = [1,9,0,1,3,0,1,0,1,0,0,0,1,0,0,0,8,0,3,1]
    arr[11] = [0,0,0,0,4,0,4,0,5,1,0,0,0,3,1,0,0,0,1,0]
    arr[12] = [0,0,0,1,0,0,1,0,0,0,1,7,1,0,3,0,0,3,0,2]
    arr[13] = [8,0,0,8,6,6,6,6,1,0,0,0,0,0,1,0,0,3,0,0]
    arr[14] = [1,0,0,0,0,0,0,0,7,0,0,1,0,0,0,0,7,1,0,1]
    arr[15] = [6,0,1,3,1,7,7,7,0,8,1,0,7,1,8,0,0,5,0,3]
    arr[16] = [0,0,0,3,0,0,1,0,0,1,7,1,5,0,5,0,0,0,1,0]
    arr[17] = [1,0,3,1,6,0,0,3,0,6,0,0,0,5,5,0,0,7,0,0]
    arr[18] = [0,0,0,0,0,6,0,1,0,0,0,0,0,1,0,1,7,0,0,2]
    arr[19] = [2,1,0,7,0,0,1,0,0,1,0,1,6,0,0,0,0,0,1,0]
    
    
    finalArr = np.array([[5, 5, 4, 4, 4, 1, 4, 4, 4, 1, 6, 6, 1, 3, 3, 1, 2, 1, 4, 1]
              , [5, 5, 4, 1, 6, 6, 3, 4, 1, 6, 6, 6, 6, 3, 1, 3, 2, 4, 4, 4]
              , [5, 1, 5, 5, 6, 6, 3, 3, 8, 8, 1, 4, 4, 4, 2, 3, 3, 9, 9, 3]
              , [7, 7, 5, 5, 5, 6, 6, 8, 8, 8, 8, 8, 4, 1, 2, 1, 9, 9, 1, 3]
              , [7, 7, 7, 7, 1, 4, 1, 2, 1, 8, 1, 7, 7, 7, 1, 9, 9, 9, 9, 3]
              , [7, 1, 9, 9, 4, 4, 4, 2, 6, 6, 6, 7, 7, 7, 7, 4, 4, 1, 9, 1]
              , [5, 5, 9, 9, 9, 9, 1, 6, 6, 6, 1, 5, 5, 1, 8, 8, 4, 4, 3, 3]
              , [5, 5, 5, 1, 9, 9, 9, 5, 5, 4, 4, 5, 5, 5, 8, 8, 8, 1, 3, 1]
              , [3, 1, 4, 4, 1, 5, 5, 5, 1, 4, 4, 6, 6, 6, 8, 8, 8, 4, 4, 4]
              , [3, 3, 4, 4, 3, 3, 4, 4, 4, 1, 6, 6, 6, 1, 5, 5, 1, 3, 1, 4]
              , [1, 9, 9, 1, 3, 4, 1, 4, 1, 7, 7, 7, 1, 5, 5, 5, 8, 3, 3, 1]
              , [9, 9, 9, 9, 4, 4, 4, 5, 5, 1, 7, 7, 7, 3, 1, 8, 8, 8, 1, 2]
              , [9, 9, 9, 1, 6, 6, 1, 5, 5, 5, 1, 7, 1, 3, 3, 8, 8, 3, 3, 2]
              , [8, 8, 8, 8, 6, 6, 6, 6, 1, 8, 8, 8, 8, 8, 1, 8, 8, 3, 5, 5]
              , [1, 6, 8, 8, 8, 8, 7, 7, 7, 8, 8, 1, 7, 7, 7, 7, 7, 1, 5, 1]
              , [6, 6, 1, 3, 1, 7, 7, 7, 7, 8, 1, 7, 7, 1, 8, 8, 8, 5, 5, 3]
              , [6, 6, 6, 3, 3, 6, 1, 3, 3, 1, 7, 1, 5, 5, 5, 8, 8, 8, 1, 3]
              , [1, 3, 3, 1, 6, 6, 6, 3, 6, 6, 7, 7, 7, 5, 5, 8, 8, 7, 7, 3]
              , [2, 3, 7, 7, 7, 6, 6, 1, 6, 6, 7, 7, 6, 1, 6, 1, 7, 7, 7, 2]
              , [2, 1, 7, 7, 7, 7, 1, 6, 6, 1, 7, 1, 6, 6, 6, 6, 7, 7, 1, 2]])
    
    
    almostComplete = finalArr.copy()
    almostComplete[19][19] = 0
    
    return Board(rows=rows, columns=columns,
                 initialValues=arr,
                 finalValues=finalArr)
    
    #return Board(rows=rows, columns=columns,
    #             initialValues=almostComplete,
    #             finalValues=finalArr)
  
  @staticmethod
  def getExampleFinishedBoard():
    """ Return a finished board for testing purposes """
    
    board = Board.getExampleBoard()
    board.values = board.finalValues
    board.updateGroups()
    return board
  
  @staticmethod
  def createBoard(rows, columns, **kwargs):
    """ Create a board using lists """
    
    # need initial and final board values
    initialBoardList = kwargs.get("initial_board", None)
    finalBoardList   = kwargs.get("final_board", None)
    if initialBoardList is None or finalBoardList is None:
      raise ValueError("Must supply both initial_values and final_values")
    
    initialArr = np.zeros((rows, columns), np.int8)
    finalArr   = np.zeros((rows, columns), np.int8)

    # convert the lists to arrays
    for row in range(rows):
      for column in range(columns):
        initialArr[row][column] = initialBoardList[row*rows + column]
        finalArr[row][column]   = finalBoardList[row*rows + column]
    
    
    # create the board
    board = Board(rows=rows, columns=columns,
                  initialValues=initialArr,
                  finalValues=finalArr)
    
    # add stats
    boardStats = kwargs.copy()
    del boardStats["initial_board"]
    del boardStats["final_board"]
    board.setBoardStats(**boardStats)
    
    """
    # set its values
    for row in range(rows):
      for column in range(columns):
        board.values[row][column] = boardList[row*rows + column]
    
    # set this as the initial state
    board.initialValues = board.values.copy()
    """
    
    return board
  
  
  def __init__(self, rows, columns, initialValues=None, finalValues=None):
    """
    # -initialValues: (array)
    # -finalValues:   (array)
    # -stats:         (dictionary)
    #
    """
    
    # if no initial values given then set to 0s (all blank)
    if initialValues is None:
      initialValues = np.zeros((rows, columns), np.int8)
      
    self.stats = {}
    
    self.rows    = rows
    self.columns = columns
    self.values  = initialValues.copy()
    
    self.initialValues = initialValues
    self.finalValues   = finalValues
    
    # groups:
    #  -groups with the correct number of members
    #  -groups with more than the max number of members
    #  -all other groups
    self.invalidGroups = {}
    self.validGroups   = {}
    self.orphanGroups  = {}
    
    # gather the group information
    self.updateGroups()
    
  def __deepcopy__(self, memodict={}):
    """ Make a copy of this board """
    
    newBoard = Board(rows          = self.rows,
                     columns       = self.columns,
                     initialValues = self.initialValues,
                     finalValues   = self.finalValues)
    
    # copy the stats
    newBoard.setBoardStats(**self.stats)
    
    # copy the current values
    newBoard.values = self.values.copy()
    
    # copy the group info
    newBoard.invalidGroups.update(self.getInvalidGroups())
    newBoard.validGroups.update(self.getValidGroups())
    newBoard.orphanGroups.update(self.getOrphanGroups())
    
    return newBoard
  

  def getBoardDimensions(self): return self.values.shape
  def getCellValue(self,row,col): return self.values.item(row,col)
  def getFinalValues(self): return self.finalValues
  def getInitialValues(self): return self.initialValues
  def getInvalidGroups(self): return self.invalidGroups
  def getOrphanGroups(self):  return self.orphanGroups
  def getValues(self):        return self.values
  def getValidGroups(self):   return self.validGroups
  
  def getBoardStats(self, statName):
    return self.stats.get(statName, None)
  
  def setBoardStats(self, **kwargs):
    self.stats.update(kwargs)
  
  def isInitialCell(self, row, column):
    """ Was this cell initialised with a value """
    return self.initialValues.item(row, column) != 0

  def isBoardComplete(self):
    """ Is the board complete """
  
    # complete when we have no orphans or invalid groups
    numOrphans = np.sum([len(v) for _, v in self.getOrphanGroups().items()])
    numInvalid = np.sum([len(v) for _, v in self.getInvalidGroups().items()])
    return numOrphans == numInvalid == 0
  
  def isBoardValid(self):
    """ Does the board have no invalid groups """
    numInvalid = np.sum([len(v) for _, v in self.getInvalidGroups().items()])
    return numInvalid == 0
  
  def resetBoard(self):
    """ Resets the board to its initial values """
    
    # set the values
    self.values = self.initialValues.copy()
    
    # update the groups
    self.updateGroups()
    
    
  def updateCell(self, x, y, value, updateGroups=True, updateInitialCells=False):
    """ Update the value of an individual cell """
    
    # can't update initial value cells unless overridden
    if self.initialValues[x][y] != 0 and not updateInitialCells:
      return
    
    # update cell and the group info
    self._setCellValue(x, y, value)
    if updateGroups: self.updateGroups()
    
  
  def clearErrors(self):
    """
    # Find the differences between the current and final values and set any differences to 0
    """
    
    #print(self.values)
    
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
    """ Set the value of an individual cell """
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
    
    # look at each cell
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
  