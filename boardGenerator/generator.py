import logging
logger = logging.getLogger(__name__)

import copy
import datetime

import numpy as np

from scipy import signal

from fillomino.board import Board


class GenerationFailedError(Exception):
  pass

class CellList(object):
  """
  # Treat a dictionary as a list to get the dicionary speed-up, but with
  # the easier list operations
  """
  
  @staticmethod
  def filledList(rows, columns):
    """ Return a CellList of all possible (row,col) locations """
    cellList = CellList()
    cellList.cells = {row:{col:True for col in range(columns)} for row in range(rows)}
    return cellList
  
  def __init__(self):
    self.cells = {}
  
  def append(self, item):
    """ Add a cell """
    
    row, col = item
    rowCells        = self.cells.get(row, {})
    rowCells[col]   = True
    self.cells[row] = rowCells
  
  def remove(self, item):
    """ Remove a cell """
    if self.__contains__(item):
      row, col = item
      del self.cells[row][col]
      if len(self.cells[row]) == 0:
        del self.cells[row]
  
  def pop(self):
    """ Pop a cell from somewhere """
    for row,col in iter(self):
      del self.cells[row][col]
      if len(self.cells[row]) == 0:
        del self.cells[row]
      return row,col
    return None
  
  def randomCell(self):
    """ Return a randomly chosen cell """
    
    allCells   = (list(iter(self)))
    cellChoice = np.random.randint(0, len(allCells))
    return allCells[cellChoice]
    
  def __deepcopy__(self, memodict={}):
    newCopy = CellList()
    newCopy.cells = copy.deepcopy(self.cells)
    return newCopy
  
  def __contains__(self, item):
    row, col = item
    return bool(self.cells.get(row)) and bool(self.cells.get(row).get(col))
  
  def __iter__(self):
    """ Iterate over cells """
    for k1,v1 in self.cells.items():
      if v1:
        for k2,_ in v1.items():
          yield k1,k2
  
  def __bool__(self):
    return bool(self.cells)
  
  def __len__(self):
    size = 0
    for _,v in self.cells.items():
      size += len(v)
    return size
  
  def __str__(self):
    
    # empty list
    if not self.cells:
      return "[]"
    
    op = "["
    for row,col in iter(self):
      op += "({},{}), ".format(row, col)
    return op[:-2] + "]"
  
  
class BoardGenerator(object):
  
  # max times to try creating a new random group within a blank region
  MAX_GROUP_CREATION_ATTEMPTS = 200
  
  # max times to try and randomly fill a small region when an initial fill fails
  MAX_FILL_SMALL_REGION_ATTEMPTS = 10
  
  @staticmethod
  def _cellsAreNeighbours(row1, column1, row2, column2):
    """ Are the two cells beside each other """
    return (row1+1, column1) == (row2, column2) or\
           (row1-1, column1) == (row2, column2) or\
           (row1, column1+1) == (row2, column2) or\
           (row1, column1-1) == (row2, column2)
  
  
  @staticmethod
  def _groupNeighbourCellsTogether(cellList):
    """ Given a list of cells, return a list of connected cell groups """

    cellList = copy.deepcopy(cellList)
    
    # list of connected cell groups
    groups = []
    
    while len(cellList) > 0:
      
      # start a new cell group
      cellGroup = CellList()
      cellGroup.append(cellList.pop())
      
      # for each candidate neighbour cell
      for cell in cellList:
        
        # if the candidate cell is touching any of the cells in this group
        for cellInGroup in cellGroup:
          if BoardGenerator._cellsAreNeighbours(*cellInGroup, *cell):
            
            # add candidate to our group
            cellGroup.append(cell)
            break
            
      
      # if we added any cells to our group, remove them from the candidate list
      if len(cellGroup) > 1:
        for cell in cellGroup:
          cellList.remove(cell)
      
      # add this group to our overall list of groups
      groups.append(cellGroup)
    
    return groups
  
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
  def newRandomGroup(board, cellList):
    """
    # Create a new, random-sized group in the cells given
    """

    regionSize = len(cellList)
    
    #groups = list(range(2,10))
    #groupWeights = [0.05, 0.1, 0.1, 0.15, 0.15, 0.15, 0.15, 0.15]
    
    creationAttempts = 0
    while True:
      
      localCellList = copy.deepcopy(cellList)
      
      # pick a random group size
      groupSize = np.random.randint(2, min(regionSize, 9))
      #groupSize = np.random.choice(groups, p=groupWeights)
      
      # pick a random cell to start from
      row, column = localCellList.randomCell()
      
      #print("row", row)
      #print("column", column)
      #print("groupSize", groupSize)
      
      # create the group
      newGroup = BoardGenerator._walkFreeCells(row, column, localCellList, limit=groupSize)
      #for c in newGroup:
      #  print(c)
      #print(cellList)
      #print("=====")
      # add the group to the board
      board = BoardGenerator.assignNumber(board, groupSize, newGroup, updateGroups=False)
      board.updateGroups()
      
      # if the board is valid after adding the new group, then then we're good
      if board.isBoardValid():
        break
      
      # board is invalid, so undo our group add:
      board = BoardGenerator.assignNumber(board, 0, newGroup, updateGroups=False)

      creationAttempts += 1
      if creationAttempts > BoardGenerator.MAX_GROUP_CREATION_ATTEMPTS:
        raise GenerationFailedError("Reached the maximum number of failed attempts to fill a region")
      
    return board, newGroup
    
    # add in a full, randomly meandering group of X
    #  -X is randomly chosen (for each attempt)
    #  -make sure board is still valid
    #    -if not, re-do meandering group
    # groupSize = np.random.randint(2, min(regionLen, 9))
    #bd, newCells = BoardGenerator.insertNewRandomGroup(bd, blankCellList)
  
  @staticmethod
  def assignNumber(board, number, cellList, updateGroups=True):
    """
    # Assign the <number> to all of the board's cells in <cellList>
    #  -option to skip updating the group information if we don't care about that
    #
    """
    for row,col in cellList:
      board.updateCell(row, col, number, updateGroups=updateGroups)
    return board
  
  @staticmethod
  def addInitialOnes(board, numOnes):
    """ Add in 1's at random places of the board, making sure they're all valid """
    
    # locations of cells we've added
    usedCells = CellList()
    
    # get board dimensions
    rows, columns = board.getBoardDimensions()
    
    for i in range(numOnes):
      
      # loop until we add a "1" to a valid location on the board
      while True:
        row = np.random.randint(0, rows)
        col = np.random.randint(0, columns)
        
        # make sure we haven't randomly selected this location before
        if (row, col) in usedCells:
          continue
        
        # set the location to 1
        board.values.itemset(row, col, 1)
      
        # make sure we haven't created a group of island 1's
        if not BoardGenerator.hasIslandOnes(board):
        
          # if the board is still valid after our change, move on
          board.updateGroups()
          if board.isBoardValid():
            usedCells.append((row, col))
            break
      
        # we made the board invalid, so undo our change
        board.values.itemset(row, col, 0)

    
    # return the board and the new cell location
    return board, usedCells
  
  
  @staticmethod
  def findBlankRegions(freeCells):
    """
    # Find number of "blank" regions we have. Walk along the freeCells list
    # until we run out of cells or walk into a previously visited cell.
    #
    # Idea is split a group of freeCells up into 1 or more connected regions.
    #
    # -freeCells: (CellList) of blank cells
    #
    """
    
    # create a copy of the free cells so we can alter it
    freeCells = copy.deepcopy(freeCells)
    
    blankRegions = []
    
    # walk along the freeCells
    while freeCells:
      
      # remove a free cell
      row, column = freeCells.pop()
      
      # walk from this cell, along all the connected free cells, in order to
      # find the extent of this blank region
      blankRegions.append(BoardGenerator._walkFreeCells(row, column, freeCells))
    
    # return all the blank regions we found
    return blankRegions
  
    
  @staticmethod
  def _walkFreeCells(row, column, freeCells, visitedCells=None, limit=None):
    """
    # Starting from (row,column), walk along the cells in <freeCells>,
    # ignoring the cells we've already visited.
    #  -returns the list of cells we walked along
    #
    # -row:          (int) row of current cell
    # -column:       (int) column of current cell
    # -freeCells:    (CellList) of cells we can walk to
    # -visitedCells: (CellList) of cells we've already been to on this walk
    # -limit:        (int) max number of cells to walk
    #
    """
    
    if visitedCells is None:
      visitedCells = CellList()
    
    # visited our start cell
    visitedCells.append((row, column))
    
    # if we've reached the limit
    if limit is not None and len(visitedCells) == limit:
      return visitedCells
    
    # try walking N, S, E, W
    directions = [(row, column+1), (row, column-1), (row+1, column), (row-1, column)]
    np.random.shuffle(directions)
    for newRow, newColumn in directions:
  
      # next cell location is valid if it:
      #  -is a free cell
      #  -hasn't already been visited
      if (newRow, newColumn) in freeCells and (newRow, newColumn) not in visitedCells:
        
        # remove next cell from free cells and walk to it
        freeCells.remove((newRow, newColumn))
        BoardGenerator._walkFreeCells(newRow, newColumn, freeCells, visitedCells, limit=limit)
        
        if limit is not None and len(visitedCells) == limit:
          break
        
    return visitedCells
  
  
  @staticmethod
  def populateRegions(board, freeCells):
    """
    # Break the list of free cells into contiguous "blank" regions. For each
    # blank region, add a randomly-sized number-group. See how many blank
    # sub-regions there are now, adding them back into the master blankRegion list.
    #
    # Will end up with a mostly-populated grid, with a few lone patches of un-filled
    # cells.
    #
    """
    logger.debug("populating regions")
    
    # list of cell groups that couldn't be filled in the random group-adding
    #  -will be of size 9 or smaller
    loneGroupList = []
    
    # find number of "blank" regions we have
    blankRegionList = BoardGenerator.findBlankRegions(freeCells)
    
    while len(blankRegionList) > 0:
    
      # get (remove) region from blankList
      blankCellList = blankRegionList.pop()
    
      regionSize = len(blankCellList)
    
      # if the region is one cell in size, add it to our list of lone groups
      if regionSize == 1:
        loneGroupList.append(blankCellList)
    
      # if region is exactly [2-9]
      elif regionSize < 10:
      
        # fill this region with a group of that size, or smaller if that's invalid
        board, usedCells = BoardGenerator.fillSmallRegion(board, blankCellList)
      
        # remove the newly added cells from our list of available cells
        for usedCell in usedCells:
          blankCellList.remove(usedCell)
      
        # couldn't fill this (whole) region
        if len(blankCellList) > 0:
        
          # group the left over cells into contiguous groups, and add
          # each group to the loneGroupList
          for group in BoardGenerator._groupNeighbourCellsTogether(blankCellList):
            loneGroupList.append(group)
    
      # insert a new group to try and break up the region
      else:
      
        # add in a randomly meandering group of X cells
        board, usedCells = BoardGenerator.newRandomGroup(board, blankCellList)
      
        # remove the newly added cells from our list of available cells
        for usedCell in usedCells:
          blankCellList.remove(usedCell)
      
        # find number of "blank" regions we have in this region
        #  -append them to end of blankList
        blankRegionList += BoardGenerator.findBlankRegions(blankCellList)
    
    
    # return our mostly-filled board and our list of loneGroups
    return board, loneGroupList
  
  def generate(self):
    """ Generate a new board """
    
    startTime = datetime.datetime.utcnow()
    
    # create a new blank board
    bd = Board(rows=self.rows, columns=self.columns)
    
    # add in some random 1's
    numOnesLowerBound = int(np.ceil(self.rows * self.columns * 0.15))
    numOnesUpperBound = int(np.ceil(self.rows * self.columns * 0.20))
    numOnes = np.random.randint(numOnesLowerBound, numOnesUpperBound)
    bd, usedCells = BoardGenerator.addInitialOnes(bd, numOnes)
    logger.debug("{} one-cells".format(numOnes))
    
    # list of all available cells
    freeCells = CellList.filledList(self.rows, self.columns)

    # remove the newly added 1-cells from our list of available cells
    for usedCell in usedCells:
      freeCells.remove(usedCell)
    
    # fill most of the board by breaking the blank cells down into
    # contiguous groups and filling the space with randomly-sized
    # number groups
    bd, loneGroupList = BoardGenerator.populateRegions(bd, freeCells)
    
    # if we have lone groups of cells that we couldn't fill, try to
    # merge them into their neighbour's groups
    logger.debug("{} lone cell groups".format(len(loneGroupList)))
    for iCell, loneGroup in enumerate(loneGroupList):
      
      # try to add the cell to the (N,S,W,E)
      try:
        bd = BoardGenerator.mergeLoneGroup(bd, loneGroup)
        
      except GenerationFailedError:
        cellsRemaining = len(loneGroupList)-iCell
        timeTaken      = datetime.datetime.utcnow() - startTime
        errMsg  = "Could not merge final cells.\n"
        errMsg += "Time taken: {}\n".format(timeTaken)
        errMsg += "Lone cells remaining: {}\n".format(cellsRemaining)
        errMsg += "Board:\n{}".format(bd.getValues())
        logger.debug("GenerationFailedError: {}".format(errMsg))
        raise GenerationFailedError(errMsg)
    
    # calculate the time taken
    timeTaken = datetime.datetime.utcnow() - startTime
    logger.debug("Board done. Time taken: {}".format(timeTaken))
    
    # final board update and checks
    bd.updateGroups()
    if not (bd.isBoardValid() and bd.isBoardComplete()):
      errMsg  = "Generation finished, but the board is not valid and complete\n"
      errMsg += "Board:\n{}".format(bd.getValues())
      raise SystemError(errMsg)
    
    # create the initial state of the board
    bd = BoardGenerator.defineInitialBoardState(bd)
    
    return bd
  
  
  @staticmethod
  def mergeLoneGroup(board, cellList):
    """
    # Try to merge a group of blank cells into one of their neighbours
    #
    #
    #
    """
    logger.debug("lone cells: {}".format(cellList))
    
    # dimensions of grid
    maxRows, maxColumns = board.getBoardDimensions()
    
    neighbourGroups = []
    
    # for each cell in the group
    for row, col in cellList:
      
      # look at each of its neighbours
      for neighRow, neighCol in [(row+1, col), (row-1, col), (row, col+1), (row, col-1)]:
        
        # if the neighbour is a valid cell
        if 0 <= neighRow < maxRows and 0 <= neighCol < maxColumns:
          
          # get the group's size/value
          groupSize = board.getCellValue(neighRow, neighCol)
          
          # skip blank cells and cells we can't expand into
          if groupSize == 0 or groupSize + len(cellList) > 9:
            continue
            
          # look through all of the board's groups of this size
          for group in board.getValidGroups()[groupSize]:
            
            # if we've found the group our neighbour belongs to
            if (neighRow, neighCol) in group:
  
              # add group to our list if we don't already have a record of it
              if group not in neighbourGroups:
                neighbourGroups.append(group)
                
              break
          
    
    logger.debug("neighbours:")
    for neigh in neighbourGroups:
      logger.debug("{} - {}".format(len(neigh), neigh))
    
    # if none of the neighbours are the same size as this group, just fill
    # in this group
    if len(cellList) not in [len(group) for group in neighbourGroups]:
      logger.debug("filling in group")
      board, success = BoardGenerator._tryAssignment(board, len(cellList), cellList)
      return board
    
    # try merging with each of our neighbours in turn
    for group in neighbourGroups:
      
      # create a new, merged group
      newGroup = copy.deepcopy(group)
      for cell in cellList:
        newGroup.append(cell)
      
      # try to create the new group
      board, success = BoardGenerator._tryAssignment(board, len(newGroup), newGroup)
      if success:
        return board
      
      # merging failed, so revert the original group
      board = BoardGenerator.assignNumber(board, len(group), group, updateGroups=False)
      board.updateGroups()
      
    # no luck merging
    msg = "Could not merge lone cell group: {}".format(cellList)
    logger.debug(msg)
    raise GenerationFailedError(msg)
    
  @staticmethod
  def _tryAssignment(board, regionSize, cellList):
    """
    # Fill cells with a number and check if the board is valid, reverting
    # the changes if it isn't
    #  -returns the board and whether the assignment was successful
    """
    
    # assign the cells
    board = BoardGenerator.assignNumber(board, regionSize, cellList, updateGroups=False)
    board.updateGroups()
    
    # if we were successful, return
    if board.isBoardValid():
      return board, True
    
    # if we failed, revert the changes and return
    else:
      board = BoardGenerator.assignNumber(board, 0, cellList, updateGroups=False)
      board.updateGroups()
      return board, False
  
  
  @staticmethod
  def _findIndicesToRemove(groupNum, probToKeep):
    
    # total number to key (at least 1)
    numToKeep = max(1, int(np.sum(np.random.binomial(1, probToKeep, groupNum))))
    print(groupNum, "-", numToKeep)
    
    # randomly choose <total-numToKeep> cells to remove
    return np.random.choice(list(range(groupNum)), groupNum - numToKeep, replace=False)

  @staticmethod
  def _removeSparseAreas(rows, columns, cellList):
    
    # turn the empty cells into a rows x columns matrix
    boardVals = np.zeros((rows, columns))
    for cell in cellList:
      boardVals.itemset(*cell, 1)
    
    # convolution filter looking for areas that will create an empty grid
    emptyRow = int(np.floor(rows/10)) + 1
    emptyCol = int(np.floor(columns/10)) + 1
    emptyGrid = np.ones((emptyRow, emptyCol))
    print(emptyGrid)
    print("++++++++++")

    # find emptiness
    matches = signal.convolve2d(boardVals, emptyGrid, mode="same")
    
    print("matches", emptyGrid.size-1)
    print(matches >= emptyGrid.size-1)
    print("--------")
    print(matches)
    print("--------")
    print(boardVals)
    print("--------")
    
    # remove the gaps in the matrix
    for row, col in list(zip(*np.where(matches >= emptyGrid.size-1))):
      boardVals.itemset(row, col, 0)
    print(boardVals)

    print("=============================")
    
    # turn the matrix back into a cell list
    newCellList = CellList()
    for row, col in list(zip(*np.where(boardVals == 1))):
      newCellList.append((row, col))
    
    return newCellList
  
  @staticmethod
  def defineInitialBoardState(board):
    """
    # Define the initial state of a finished board
    #
    # Remove X cells from each finished group, where the probability of a
    # cell being removed is proporitional to the group size (+- some magic)
    #
    # -board: (Board) where the current values are that of a valid, completed board
    """
    
    # make sure the board is complete
    if not board.isBoardComplete():
      raise SystemError("Was passed an in-complete board")
    
    board = copy.deepcopy(board)
    
    # make sure the final values are set
    board.finalValues = board.values.copy()
    
    # completed number groups
    groups = board.getValidGroups()
    
    # list of cells we will remove
    toRemove = CellList()
    
    # probabilities to keep a cell in each numbered group
    probToKeep = {
      2: 1/2,
      3: 1/3,
      4: 1/4,
      5: 1/(5-1),
      6: 1/(6-1),
      7: 1/(7-1),
      8: 1/(8-2),
      9: 1/(9-2)
    }

    # for each numbered group
    for groupNum in range(2,10):
      for group in groups[groupNum]:
        
        # randomly find X cells to remove, keeping at least one cell per group
        for indexToRemove in BoardGenerator._findIndicesToRemove(groupNum, probToKeep[groupNum]):
          toRemove.append(group[indexToRemove])
    
    
    # make sure the grid isn't too sparse by populating "empty" regions
    rows, columns = board.getBoardDimensions()
    toRemove = BoardGenerator._removeSparseAreas(rows, columns, toRemove)
    
    # blank out the board cells we have decided to remove
    for cellToRemove in toRemove:
      board.updateCell(*cellToRemove, 0, updateGroups=False, updateInitialCells=True)
      board.updateGroups()
    
    # set the initial values
    board.initialValues = board.values.copy()
    
    return board
  
  
  @staticmethod
  def fillSmallRegion(board, cellList):
    """
    # Fill in a small region (2-9 cells) with a single group. Tries successively
    # smaller groups if the initial fill is invalid.
    #  -returns the board and a list of cells we have filled (if any)
    #
    """

    regionSize = len(cellList)
    
    # try filling the region with a group of exactly that size
    board, success = BoardGenerator._tryAssignment(board, regionSize, cellList)
    if success:
      return board, copy.deepcopy(cellList)
    
    # try smaller regions
    for smallerRegion in range(regionSize, 1, -1):
      
      # try a few random walks to fill this smallerRegion
      for _ in range(BoardGenerator.MAX_FILL_SMALL_REGION_ATTEMPTS):
        
        # start at a random cell
        row, column = cellList.randomCell()
        
        # walk for <smallerRegion> number of cells
        walkList = BoardGenerator._walkFreeCells(row, column, copy.deepcopy(cellList), limit=smallerRegion)
        
        # try filling this sub-region
        board, success = BoardGenerator._tryAssignment(board, smallerRegion, walkList)
        if success:
          return board, walkList
      
    # no luck
    return board, CellList()


    