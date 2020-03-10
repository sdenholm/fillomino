
import unittest

import datetime
import os

import numpy as np

from fillomino.database import Database, DatabaseInfo

class test_Database(unittest.TestCase):
  
  # perform all tests in this class
  TEST_ALL = True
  
  @classmethod
  def setUpClass(cls):
    pass
  
  def setUp(self):
    self.dbName = "testDB.db"
    
    # make sure the test database already exists
    if os.path.exists(self.dbName):
      raise FileExistsError("test database {} already exists")

    # create a test database
    DatabaseInfo.createDatabase(self.dbName)
    self.db = Database(self.dbName)
    self.db.connect()
  
  
  def tearDown(self):
    
    # close the database
    if self.db:
      self.db.close()
    
    # delete the test database
    if os.path.exists(self.dbName):
      os.remove(self.dbName)
  
  
  @staticmethod
  def _storeBoards(db, numBoards, **kwargs):
    
    rows    = kwargs.get("rows", 20)
    columns = kwargs.get("columns", 20)
    
    # store <numBoards> boards
    for boardID in range(1,numBoards+1):
      
      # store the board
      initialBoard = [boardID % 9]*rows*columns
      finalBoard   = [(boardID+1) % 9]*rows*columns
      creationDate = str(datetime.datetime.utcnow())
      stats        = {"c": boardID + 2, "d": boardID + 3}
      db.storeBoard(rows=rows,
                    columns=columns,
                    boardID=boardID,
                    initialBoard=initialBoard,
                    finalBoard=finalBoard,
                    creationDate=creationDate,
                    stats=stats)
      
      
  
  #
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_storeAndLoad(self):
    """ Storing and loading boards works """

    maxTests = 50
    rows     = 10
    columns  = 10
    
    # store and load <maxTests> boards and make sure they are the same
    boardIDList = map(int, set(np.random.randint(1,1000,maxTests)))
    for boardID in boardIDList:
      
      # store the board
      initialBoard = [boardID % 9]*rows*columns
      finalBoard   = [(boardID+1) % 9]*rows*columns
      creationDate = str(datetime.datetime.utcnow())
      stats        = {"c": boardID + 2, "d": boardID + 3}
      storeRet = self.db.storeBoard(rows=rows,
                                    columns=columns,
                                    boardID=boardID,
                                    initialBoard=initialBoard,
                                    finalBoard=finalBoard,
                                    creationDate=creationDate,
                                    stats=stats)
      
      
      
      # load the board
      loadedBoard = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      
      # TEST: boards are the same
      self.assertIsNotNone(loadedBoard)
      self.assertListEqual(initialBoard, loadedBoard.getInitialValues().flatten().tolist())
      self.assertListEqual(finalBoard, loadedBoard.getFinalValues().flatten().tolist())
      self.assertDictEqual(stats, loadedBoard.getBoardStats("stats"))


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_duplicateBoardIDs(self):
    """ Can't store a board with a duplicate ID """
    
    rows    = 20
    columns = 20

    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
    
    # TEST: storing boards with IDs 1-10 fails
    for boardID in range(1,11):
      
      # store the board
      initialBoard = [boardID % 9]*rows*columns
      finalBoard   = [(boardID+1) % 9]*rows*columns
      creationDate = str(datetime.datetime.utcnow())
      stats        = {"c": boardID + 2, "d": boardID + 3}
      
      args = {
        "rows":         rows,
        "columns":      columns,
        "boardID":      boardID,
        "initialBoard": initialBoard,
        "finalBoard":   finalBoard,
        "creationDate": creationDate,
        "stats":        stats
      }
      
      # TEST: store fails
      self.assertRaises(SystemError, self.db.storeBoard, **args)

    
    # TEST: storing boards with IDs >10 succeeds
    for boardID in range(11, 21):
      # store the board
      initialBoard = [boardID % 9]*rows*columns
      finalBoard   = [(boardID+1) % 9]*rows*columns
      creationDate = str(datetime.datetime.utcnow())
      stats        = {"c": boardID + 2, "d": boardID + 3}
  
      args = {
        "rows":         rows,
        "columns":      columns,
        "boardID":      boardID,
        "initialBoard": initialBoard,
        "finalBoard":   finalBoard,
        "creationDate": creationDate,
        "stats":        stats
      }

      # TEST: store succeeds
      self.assertIsNotNone(self.db.storeBoard(**args))


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_nonExistantBoardIDs(self):
    """ Can't load a board with an invalid ID """
    
    rows    = 20
    columns = 20
    
    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
    
    # TEST: load a board with a valid ID succeeds
    for boardID in range(1,11):
      loadRet = self.db.loadBoard(rows=rows, columns=columns, boardID=1)
      self.assertIsNotNone(loadRet)

    # TEST: load a board with an invalid ID fails
    for boardID in range(11, 21):
      loadRet = self.db.loadBoard(rows=rows, columns=columns, boardID=11)
      self.assertIsNone(loadRet)


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_loadRandomBoard(self):
    """ Load a random board """
    
    rows    = 20
    columns = 20
    
    # store 50 boards
    test_Database._storeBoards(self.db, 50, rows=rows, columns=columns)
    
    # fetch 10 random boards
    for _ in range(10):
      board = self.db.loadRandomBoard(rows=rows, columns=columns)
      
      # TEST: board was returned okay
      self.assertIsNotNone(board)
      self.assertIn(board.getID(), range(1, 51))


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_loadRandomBoardExclude(self):
    """ Load a random board that doesn't have a given ID"""
  
    rows = 20
    columns = 20
  
    # store 5 boards
    test_Database._storeBoards(self.db, 5, rows=rows, columns=columns)
  
    # fetch 1000 random boards to see if we get the excluded board
    #   -chance of false positive is about 1 in 4,909,093,465...
    for _ in range(1000):
      board = self.db.loadRandomBoard(rows=rows, columns=columns, excludeID=1)
    
      # TEST: board was returned okay
      self.assertIsNotNone(board)
      self.assertNotEqual(board.getID(), 1)

  
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_loadUnsolvedBoard(self):
    """ Load a random, unsolved board """
  
    rows = 20
    columns = 20
  
    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
    
    # solve the first 8 boards and store them
    for boardID in range(1,9):
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      board.updateSolveStats(14)
      self.db.updateBoardStats(board)
      
    
    # fetch 100 random, solved boards
    for _ in range(100):
      board = self.db.loadUnsolvedBoard(rows=rows, columns=columns)
    
      # TEST: board was returned okay and not one of the ones we solved
      self.assertIsNotNone(board)
      self.assertIn(board.getID(), [9,10])


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_loadUnsolvedBoardExclude(self):
    """ Load a random, unsolved board that doesn't have a given ID"""
  
    rows = 20
    columns = 20
  
    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
  
    # solve the first 7 boards and store them
    for boardID in range(1, 8):
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      board.updateSolveStats(14)
      self.db.updateBoardStats(board)
  
    # fetch 100 random, solved boards
    #  -board can't have ID = 8
    for _ in range(100):
      board = self.db.loadUnsolvedBoard(rows=rows, columns=columns, excludeID=8)
    
      # TEST: board was returned okay and not one of the ones we solved
      self.assertIsNotNone(board)
      self.assertIn(board.getID(), [9, 10])


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_removeBoard(self):
    """ Remove a board from the database """
  
    rows = 20
    columns = 20
  
    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
    
    for boardID in range(1,6):
    
      # TEST: board with ID <boardID> was stored
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      self.assertIsNotNone(board)
      self.assertEqual(board.getID(), boardID)
    
      # delete board with ID <boardID>
      self.db.removeBoard(rows, columns, boardID)

      # TEST: board with ID <boardID> is not found
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      self.assertIsNone(board)


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_updateBoardStats(self):
    """ Board stats are updated in the database """
  
    rows    = 20
    columns = 20
  
    # store 10 boards
    test_Database._storeBoards(self.db, 10, rows=rows, columns=columns)
  
    for boardID in range(1, 6):
      
      # load a board
      board = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      
      # TEST: mean solve is null and solve count is 0
      self.assertIsNone(board.getBoardStats("solve_mean"))
      self.assertEqual(board.getBoardStats("solve_count"), 0)
      
      # update the stats and store the board
      board.updateSolveStats(14)
      self.db.updateBoardStats(board)
      
      # TEST: board loads with updated stats
      self.assertEqual(board.getBoardStats("solve_mean"), 14)
      self.assertEqual(board.getBoardStats("solve_count"), 1)


  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_getBoardsInfo(self):
    """ Correct info on all the tables we have """
    
    # random list of dimensions and number of boards
    dimCountList = []
    for _ in range(10):
      row   = np.random.randint(5, 30)
      col   = np.random.randint(5, 30)
      count = np.random.randint(5, 30)
      dimCountList.append((row, col, count))
    
    # store <count> boards for each set of board dimensions
    for rows, columns, count in dimCountList:
      test_Database._storeBoards(self.db, count, rows=rows, columns=columns)

    # get the board info
    boardInfo = self.db.getBoardsInfo()
    
    # TEST: the board info matches the boards we added
    for rows, cols, count in dimCountList:
      self.assertEqual(boardInfo[(rows,cols)]["length"], count)
