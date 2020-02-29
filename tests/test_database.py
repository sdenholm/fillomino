import os
import unittest

import numpy as np

from fillomino.database import Database, DatabaseSetup

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
    DatabaseSetup.createDatabase(self.dbName)
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
      initialBoard = {"a": boardID}
      finalBoard = {"b": boardID + 1}
      stats = {"c": boardID + 2, "d": boardID + 3}
      db.storeBoard(rows=rows,
                    columns=columns,
                    boardID=boardID,
                    initialBoard=initialBoard,
                    finalBoard=finalBoard,
                    stats=stats)
  
  #
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_storeAndLoad(self):
    """ Storing and loading boards works """

    maxTests = 50
    rows     = 20
    columns  = 20
    
    # store and load <maxTests> boards and make sure they are the same
    boardIDList = map(int, set(np.random.randint(1,1000,maxTests)))
    for boardID in boardIDList:
      
      # store the board
      initialBoard = {"a":boardID}
      finalBoard   = {"b":boardID+1}
      stats        = {"c":boardID+2, "d":boardID+3}
      storeRet = self.db.storeBoard(rows         = rows,
                                    columns      = columns,
                                    boardID      = boardID,
                                    initialBoard = initialBoard,
                                    finalBoard   = finalBoard,
                                    stats        = stats)
      
      # load the board
      loadRet = self.db.loadBoard(rows=rows, columns=columns, boardID=boardID)
      
      # TEST: boards are the same
      self.assertIsNotNone(loadRet)
      self.assertDictEqual(initialBoard, loadRet["initialBoard"])
      self.assertDictEqual(finalBoard, loadRet["finalBoard"])
      self.assertDictEqual(stats, loadRet["stats"])


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
      initialBoard = {"a": boardID}
      finalBoard = {"b": boardID + 1}
      stats = {"c": boardID + 2, "d": boardID + 3}
      
      args = {
        "rows":         rows,
        "columns":      columns,
        "boardID":      boardID,
        "initialBoard": initialBoard,
        "finalBoard":   finalBoard,
        "stats":        stats
      }
      
      # TEST: store fails
      self.assertRaises(SystemError, self.db.storeBoard, **args)

    
    # TEST: storing boards with IDs >10 succeeds
    for boardID in range(11, 21):
      # store the board
      initialBoard = {"a": boardID}
      finalBoard = {"b": boardID + 1}
      stats = {"c": boardID + 2, "d": boardID + 3}
  
      args = {
        "rows": rows,
        "columns": columns,
        "boardID": boardID,
        "initialBoard": initialBoard,
        "finalBoard": finalBoard,
        "stats": stats
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
      boardInfo = self.db.loadRandomBoard(rows=rows, columns=columns)
      
      # TEST: board was returned okay
      self.assertIsNotNone(boardInfo)
      self.assertIn(boardInfo["id"], range(1, 50))
      