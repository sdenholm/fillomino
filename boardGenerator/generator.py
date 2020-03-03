import datetime

from scipy import signal

import numpy as np

from fillomino.board import Board


class GenerationFailedError(Exception):
  pass

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
    oneCells = []
    
    # get board dimensions
    rows, columns = board.getBoardDimensions()
    
    for i in range(numOnes):
      
      # loop until we add a valid "1"
      while True:
        row = np.random.randint(0, rows)
        col = np.random.randint(0, columns)
        
        # make sure we haven't randomly selected this location before
        if (row, col) in oneCells:
          continue
        
        # set the location to 1
        board.values.itemset(row, col, 1)
      
        # make sure we don't have any island 1's
        if not BoardGenerator.hasIslandOnes(board):
        
          # if the board is still valid after our change, move on
          board.updateGroups()
          if board.isBoardValid():
            oneCells.append((row,col))
            break
      
        # we made the board invalid, so undo our change
        board.values.itemset(row, col, 0)
    
    # return the board and the new cell location
    return board, oneCells
  
  def generate(self):
    
    startTime = datetime.datetime.utcnow()
    
    # create a new blank board
    bd = Board(rows=self.rows, columns=self.columns)
    
    # add in some random 1's
    numOnes = np.random.randint(40, 50)
    
    bd, oneCells = BoardGenerator.addInitialOnes(bd, numOnes)
    
    # number of free spaces
    #freeSpaces = np.product(bd.getBoardDimensions()) - numOnes
    
    # how many "blank" regions to we have
    # blankRegions = [(0,0), (0,1)...], [(3,4),3,5)...] ...]
    
    # -if any regions are exactly [2-9], make them a region of that size
    # -for each region:
    #  -add in a full, randomly meandering group of X
    #  -get blank regions in this region:
    #   -if still one large region:
    #    -add in another meandering region of size Y
    #   -else, is now 2+ small regions
    #    -loop back to start

    
    # blankRegions = [(0,0), (0,1)...], [(3,4),3,5)...] ...]

    # -find number of "blank" regions to we have
    # -get (remove) region from blankList
    #   -if region exactly [2-9]
    #     -make it a group of that size
    #   -else:
    #     -add in a full, randomly meandering group of X
    #     -make sure board is still valid
    #       -if not, re-do meandering group
    #     -find number of "blank" regions to we have
    #       -append them to end of blankList
    
    
    # remove the newly added 1-cells from our list of available cells
    allCells = [(r, c) for r in range(self.rows) for c in range(self.columns)]
    for usedCell in oneCells:
      allCells.remove(usedCell)
    
    # list of cells which got missed in the random group adding
    loneCellList = []
    
    # find number of "blank" regions we have
    blankRegionList = BoardGenerator.findBlankRegions(bd, allCells)
    
    while len(blankRegionList) > 0:
      
      # get (remove) region from blankList
      blankCellList = blankRegionList.pop()

      regionLen = len(blankCellList)
      
      # if the region is one cell in size, add it to our "to clean up" list
      if regionLen == 1:
        loneCellList.append(blankCellList[0])
      
      # if region exactly [2-9]
      elif regionLen < 10:
        
        # make it a group of that size
        bd = BoardGenerator.assignNumber(bd, regionLen, blankCellList)
      
      # insert a new group to try and break up the region
      else:
        
        # add in a full, randomly meandering group of X
        #  -X is randomly chosen (for each attempt)
        #  -make sure board is still valid
        #    -if not, re-do meandering group
        #groupSize = np.random.randint(2, min(regionLen, 9))
        bd, newCells = BoardGenerator.insertNewRandomGroup(bd, blankCellList)

        # remove the newly added cells from our list of available cells
        for usedCell in newCells:
          blankCellList.remove(usedCell)
        
        # find number of "blank" regions we have in this region
        #  -append them to end of blankList
        blankRegionList += BoardGenerator.findBlankRegions(bd, blankCellList)
    
    # if we have single, empty cells left over try to merge them into
    # their neighbour's groups
    for iCell, loneCell in enumerate(loneCellList):
      
      # try to add the cell to the (N,S,W,E)
      #  -check for invalid cell after each attempt
      #  -ignore groups == 9
      #  -if (N,S,W,E) fails:
      #    -make it a 1 (if possible)
      #    -merge it into a neighbour 1 to make a 2 (if possible)
      #    -fail(?)
      #    -try the other cells and come back later(?)
      bdNew = BoardGenerator.mergeLoneCell(bd, loneCell)
      if bdNew is None:
        cellsRemaining = len(loneCellList)-iCell
        timeTaken      = datetime.datetime.utcnow() - startTime
        errMsg  = "Could not merge final cells.\n"
        errMsg += "Time taken: {}\n".format(timeTaken)
        errMsg += "Lone cells remaining: {}\n".format(cellsRemaining)
        errMsg += "Board:\n{}".format(bd.getValues())
        raise GenerationFailedError(errMsg)
      
      else:
        bd = bdNew

    timeTaken = datetime.datetime.utcnow() - startTime
    return bd, timeTaken

    