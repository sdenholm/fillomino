
import unittest

import numpy as np

from fillomino.board import Board

class test_Board(unittest.TestCase):
  
  # perform all tests in this class
  TEST_ALL = True
  
  @classmethod
  def setUpClass(cls):
    pass
  
  def setUp(self):
    pass
  
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_get(self):
    """ The get methods return what we expect """

    numTests = 20
    
    for _ in range(numTests):
      
      boardID = int(np.random.randint(1, 10000000))
      rows    = int(np.random.randint(5, 30))
      columns = int(np.random.randint(5, 30))
      
      initialVals       = np.array([[1] * columns] * rows)
      initialVals[0][0] = 0
      finalVals         = np.array([[9] * columns] * rows)
      stats = {"id": boardID, "plus": boardID+2, "mult": boardID*2, "pow": boardID**2}
      
      
      board = Board(rows=rows,
                    columns=columns,
                    initialValues=initialVals,
                    finalValues=finalVals,
                    **stats)
      
      # TEST: board was created okay
      self.assertIsNotNone(board)


      ###########################################################################
      # TEST: get methods
      ###########################################################################
      
      # ID
      self.assertEqual(board.getID(), boardID)
      
      # dimensions
      self.assertEqual(board.getBoardDimensions(), (rows, columns))
      
      # initial and final values
      self.assertListEqual(board.getInitialValues().tolist(), initialVals.tolist())
      self.assertListEqual(board.getFinalValues().tolist(), finalVals.tolist())
      
      # values
      self.assertListEqual(board.getValues().tolist(), initialVals.tolist())
      
      # stats
      self.assertDictEqual(board.getBoardStats(), stats)
      
      # solve time
      self.assertIsNone(board.getSolveTime())
      
      # is board complete
      self.assertFalse(board.isBoardComplete())
      
      # cell values
      for row in range(rows):
        for col in range(columns):
          
          # cell values match
          self.assertEqual(board.getCellValue(row, col), initialVals.item(row, col))
          
          # all cells except (0,0) are initial
          self.assertEqual(board.isInitialCell(row, col), not(row == 0 and col ==0))

    
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_create(self):
    """ Make sure board creates correctly """
    
    def createValidArgs():
      
      boardID = int(np.random.randint(1, 10000000))
      rows    = int(np.random.randint(5, 30))
      columns = int(np.random.randint(5, 30))
  
      initialVals       = np.array([[1] * columns] * rows)
      initialVals[0][0] = 0
      finalVals         = np.array([[9] * columns] * rows)
      stats = {"id": boardID, "plus": boardID + 2, "mult": boardID * 2, "pow": boardID ** 2}
      
      validArgs = {
        "rows":          rows,
        "columns":       columns,
        "initialValues": initialVals,
        "finalValues":   finalVals,
      }
      validArgs.update(stats)
      return validArgs
    
    
    # TEST: no problems
    args = createValidArgs()
    bd = Board(**args)
    
    
    ###########################################################################
    # TEST: types
    ###########################################################################
    
    # rows
    args = createValidArgs()
    args["rows"] = "row"
    self.assertRaises(TypeError, Board, **args)
    
    # columns
    args = createValidArgs()
    args["columns"] = "columns"
    self.assertRaises(TypeError, Board, **args)
    
    # initialValues
    args = createValidArgs()
    args["initialValues"] = "initialValues"
    self.assertRaises(TypeError, Board, **args)
    
    # finalValues
    args = createValidArgs()
    args["finalValues"] = "finalValues"
    self.assertRaises(TypeError, Board, **args)
    
    
    ###########################################################################
    # TEST: values
    ###########################################################################

    # rows
    args = createValidArgs()
    args["rows"] = -1
    self.assertRaises(ValueError, Board, **args)

    # columns
    args = createValidArgs()
    args["columns"] = -1
    self.assertRaises(ValueError, Board, **args)

    # initialValues
    args = createValidArgs()
    args["initialValues"] = np.zeros((2,3))
    self.assertRaises(ValueError, Board, **args)

    # finalValues
    args = createValidArgs()
    args["finalValues"] = np.zeros((2,3))
    self.assertRaises(ValueError, Board, **args)
    

  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_reset(self):
    """ Board successfully resets """

    numTests = 20
    
    for _ in range(numTests):
    
      boardID = int(np.random.randint(1, 10000000))
      rows    = 5
      columns = 5
  
      initialVals = np.zeros((rows, columns))
      finalVals   = np.array([[5, 5, 5, 5, 5],
                              [1, 4, 4, 4, 4],
                              [5, 5, 5, 5, 5],
                              [1, 4, 4, 4, 4],
                              [5, 5, 5, 5, 5]])
      stats = {"id":   boardID,   "plus": boardID+2,
               "mult": boardID*2, "pow":  boardID**2}
  
      # create the board
      board = Board(rows          = rows,
                    columns       = columns,
                    initialValues = initialVals,
                    finalValues   = finalVals,
                    **stats)
      
      # update 20 random cells
      for _ in range(20):
        row = int(np.random.randint(1, rows))
        col = int(np.random.randint(1, columns))
        board.updateCell(row,col,5)
      
      # TEST: board was updated
      self.assertNotEqual(np.sum(list(map(abs, board.getValues().flatten().tolist()))), 0)
      
      # reset the board
      board.resetBoard()
  
      # TEST: board back to start
      self.assertEqual(np.sum(list(map(abs, board.getValues().flatten().tolist()))), 0)
      self.assertListEqual(board.getValues().tolist(), initialVals.tolist())
    

  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_isBoardValid(self):
    """ Invalid board is registered correctly """
    
    boardID = int(np.random.randint(1, 10000000))
    rows    = 5
    columns = 5
    
    finalVals = np.array([[5,5,5,5,5],[1,4,4,4,4],[5,5,5,5,5],[1,4,4,4,4],[5,5,5,5,5]])
    initialVals = finalVals.copy()
    initialVals[1][0] = 0
    stats = {"id": boardID, "plus": boardID + 2, "mult": boardID * 2, "pow": boardID ** 2}
    
    # create the board
    board = Board(rows=rows,
                  columns=columns,
                  initialValues=initialVals,
                  finalValues=finalVals,
                  **stats)
    
    # TEST: board not valid or complete
    board.updateCell(1, 0, 5)
    board.updateGroups()
    self.assertFalse(board.isBoardValid())
    self.assertFalse(board.isBoardComplete())
    
    # TEST: board is valid and complete now
    board.updateCell(1,0,1)
    self.assertTrue(board.isBoardValid())
    self.assertTrue(board.isBoardComplete())
    